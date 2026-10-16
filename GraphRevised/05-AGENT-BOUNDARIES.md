# Agent Boundaries and Governed Write Path

> **Note (2026-10-16).** The CCA, SCA, and SFA chain below is retired (curator,
> 2026-10-14; [25](25-LIVES-AND-PLAYGROUND.md) §11): agents prepare event
> inquiries ([29](29-EVENT-CENTRED-INQUIRY.md) §7), enrichers by kind replace the
> facet agents, and facets are lenses. The boundaries stand: agents propose, a
> deterministic validator checks, only the curator accepts, nothing is hidden
> (25 decision 2), and prompt and registry versions are recorded. The runtime is
> the Anthropic SDK, not LangGraph.

This document describes how agents may interact with the revised graph. It is
an orchestration design, not a reason to enlarge the core Neo4j schema.

## 1. The front door: Concierge and Command Agent

The **Concierge and Command Agent (CCA)** is the user-facing planning agent.
Its job is to translate a natural-language request into a typed inquiry plan.

Before resolving entities, the CCA must classify whether the request belongs
within Chrystallum's historical knowledge-graph scope. This prevents the
system from treating every command containing a historical noun as a request
for historical graph construction.

For example:

```text
Graph Bismark
```

may refer to:

- Otto von Bismarck;
- the German battleship Bismarck;
- another person, ship, place, organization, or namesake.

The CCA should identify the ambiguity and return candidates instead of silently
creating or enriching the wrong node.

The CCA produces an `InquiryPlan` such as:

```yaml
inquiryPlan:
  userRequest: Graph Bismark
  candidates:
    - label: Otto von Bismarck
      kind: Person
      status: candidate
    - label: Bismarck
      kind: Ship
      status: candidate
  clarificationRequired: true
  subjectId: null
  workflows: []
  facets: []
  budget:
    maxNewEntities: 10
    maxProposals: 20
```

The CCA does not:

- create accepted entities;
- create accepted subjects;
- research historical claims;
- decide disputed identity;
- execute unrestricted Cypher;
- commit Neo4j transactions.

The CCA plans and routes. It does not become an authority.

The first front-door result is a `ScopeDecision`:

```yaml
scopeDecision:
  decision: IN_SCOPE | OUT_OF_SCOPE | REFRAME_REQUIRED
  primaryIntent: HISTORICAL_GRAPH_CONSTRUCTION
  historicalOrientation: EXPLICIT
  suggestedHistoricalFrames: []
  nextAction: CREATE_INQUIRY_PLAN
```

The CCA should classify intent, not merely detect nouns. “Graph the history
of sugar” is in scope. “Graph how to bake an apple pie” is procedural and
should be redirected. “Graph sugar” is ambiguous and may require
`REFRAME_REQUIRED`.

The CCA should distinguish ordinary graph questions from connection-discovery
questions:

```text
TRACE_EXISTING_PATH
  Known endpoints; find and explain admissible committed paths.

DISCOVER_SEMANTIC_BRIDGE
  Endpoints may be remote; propose and investigate missing intermediate
  concepts without inventing durable relationships.
```

For example, “How is a Roman senator related to a mollusk?” should be routed
as `DISCOVER_SEMANTIC_BRIDGE`, not treated as a shortest-path query.

## 2. Agent chain

The proposed execution chain is:

```text
User
  ↓
Concierge and Command Agent
  ↓
InquiryPlan
  ↓
Existing SCA or SCA Factory
  ↓
Bound SubjectConcept workflow
  ↓
FacetApplications
  ↓
Subject Facet Agents
  ↓
Proposals
  ↓
SCA decisions
  ↓
Deterministic validation
  ↓
CommitCommand
  ↓
Neo4j transaction
```

This is a workflow around the graph. The graph remains valid if the workflow
is stopped, retried, or replaced.

## 3. Responsibilities by role

### CCA

```text
Plans and routes.
```

It produces an `InquiryPlan`, detects ambiguity, selects candidate workflows,
and applies an initial budget.

### SCA

```text
Coordinates and adjudicates.
```

It binds a SubjectConcept to the inquiry, selects or requests facet work,
checks duplicate subjects, evaluates proposals, and produces decisions.

The SCA may issue a commit command, but should not execute unrestricted Cypher.

### SFA

```text
Investigates and proposes.
```

An SFA works through one analytical facet. It may retrieve sources, identify
candidate entities, and propose assertions or subject candidates. It never
writes accepted knowledge directly.

What an agent proposes is visible at once, not held back until review
([25-LIVES-AND-PLAYGROUND.md](25-LIVES-AND-PLAYGROUND.md) decision 2): every
read projection shows proposed claims and entities beside accepted ones,
labelled with their status and source. Acceptance is the curator's
promotion, not a gate on being seen. Rejected, superseded, and deprecated
content is shown only in audit views.

Future source-ingestion workflows may include an Index Harvest Agent. Its
role is to interpret a machine-readable scholarly index and route cited
passages to appropriate SFAs. Parsing and persistence remain deterministic,
and the agent cannot mutate committed knowledge directly.

### Deterministic validation service

```text
Checks and commits.
```

It validates schemas, IDs, relationship direction, lifecycle transitions,
permissions, evidence requirements, and idempotency. It converts an accepted
`CommitCommand` into a bounded Neo4j transaction.

### Explanation Agent

```text
Explains the authorized graph projection.
```

It may answer questions about committed knowledge, decisions, sources, and
provenance. It must not create new knowledge while explaining the graph.

## 4. Typed interfaces

Each boundary should use a typed object rather than free-form prose.

Minimum interfaces:

```text
InquiryPlan
Proposal
Decision
CommitCommand
CommitResult
ExplanationRequest
SemanticBridgeResult
```

The exact runtime technology is deferred. Pydantic models, JSON Schema, or
another typed contract system may be used, provided the schemas are versioned.

An example commit command:

```yaml
commitCommand:
  commandId: chr:command:...
  architectureVersion: 0.1
  schemaVersion: proposal-v1
  decisionIds:
    - chr:decision:...
  operations:
    - operation: createAssertion
      assertionId: chr:assertion:...
  authorization:
    actor: deterministic-commit-service
    role: system
  idempotencyKey: ...
```

The command must contain enough information for the validator to reject an
invalid or stale proposal without asking an agent to reinterpret it.

An inquiry plan for bridge discovery may contain:

```yaml
operation: DISCOVER_CONNECTION
endpoints:
  - mention: Roman senator
    expectedType: PoliticalRole
  - mention: mollusk
    expectedType: TaxonomicClass
pathIntent:
  mode: SEMANTIC_BRIDGE_DISCOVERY
  requireHistoricalMeaning: true
  allowCrossFacetTraversal: true
  requireHopEvidence: true
constraints:
  maxHops: 7
  maxCandidatePaths: 5
  excludeGenericEdges:
    - RELATED_TO
    - ASSOCIATED_WITH
```

## 5. Prompt architecture

Agents should not receive the entire architecture document on every call.
Their runtime context should be compiled from four parts:

1. **Constitution** — small, immutable rules that apply to every agent.
2. **Role card** — responsibilities, prohibited actions, and output contract.
3. **Architecture packet** — relevant predicates, transitions, policies,
   mappings, and examples retrieved for this task.
4. **Task packet** — user request, candidates, graph neighborhood, evidence,
   budget, and available tools.

This keeps prompts smaller and makes the active rules inspectable.

Every accepted proposal should record:

```text
architecture version
constitution version
role-card version
prompt version
output-schema version
model identifier
tool versions
```

## 6. Governance registry

The system may eventually maintain a governance subgraph containing:

```text
ArchitectureVersion
AgentDefinition
AgentRole
PromptTemplate
PromptVersion
OutputSchema
PredicateDefinition
NodeTypeDefinition
LifecycleMachine
TransitionRule
PolicyRule
MappingRule
AuthorityDefinition
FacetDefinition
ToolDefinition
AccessRole
TestCase
```

This registry would answer questions such as:

- Which prompt governed this proposal?
- Which predicate rule permitted this relationship?
- Which architecture version produced the decision?
- What changed between two graph runs?

However, the governance subgraph must not be its own sole trust anchor. A
versioned bootstrap manifest outside the graph should contain at least:

- the minimum constitution;
- trusted architecture root identifiers;
- schema hashes;
- allowed tools;
- last-known-good prompt versions;
- permitted commit service identity.

The governance registry is a later capability. The clean-start graph can begin
with files and versioned schemas before storing governance definitions in
Neo4j.

## 7. MCP boundary

If MCP is introduced, expose:

```text
Resources:
  architecture packets, schemas, authority records, read-only graph views

Tools:
  typed candidate lookup, proposal submission, validation, commit requests

Prompts:
  user-selectable inquiry workflows
```

MCP tools should expose bounded operations with schemas. They must not expose a
general-purpose Cypher tool to conversational agents.

## 8. Retry and write safety

Agent execution is not exactly once. A node may be retried after an interrupt
or failure. Therefore:

- proposals require deterministic IDs;
- source observations require deterministic IDs;
- commit commands require idempotency keys;
- Neo4j writes require uniqueness constraints and `MERGE` or compare-and-set;
- validation must occur again at commit time;
- an accepted decision must not be silently altered by a retry.

The durable write boundary is:

```text
accepted decisions
  → deterministic CommitCommand
  → validation
  → one bounded Neo4j transaction
```

## 9. Access roles

The initial access model can be small:

| Role | Permitted action |
|---|---|
| Reader | Read authorized graph projections |
| CCA | Create inquiry plans |
| SFA | Submit proposals and source observations |
| SCA | Reconcile proposals and issue commit commands |
| Curator | Approve, reject, edit, merge, or override |
| Ontology administrator | Change predicates, schemas, and lifecycle rules |
| Commit service | Execute validated commit commands |
| System administrator | Manage deployment and trust configuration |

The important boundary is that proposal creation and durable graph mutation
are different permissions.

## 10. What belongs in the clean start

Implement first:

1. CCA ambiguity detection for one simple request;
2. `InquiryPlan`;
3. one SCA workflow;
4. one SFA proposal contract;
5. deterministic validation;
6. one bounded `CommitCommand`;
7. an accepted assertion connected to the temporal year backbone;
8. one bridge-discovery result that remains non-durable until its missing hops
   are separately proposed and accepted.

Defer:

- a full governance subgraph;
- autonomous prompt modification;
- unrestricted tool discovery;
- autonomous round-robin facet expansion;
- generated unrestricted graph mutations;
- an Explanation Agent that can write.
