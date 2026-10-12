# Review of the Chrystallum GraphRevised Direction
## Overall assessment
The refactoring is moving in the right direction. `GraphRevised` is no longer trying to pre-model the whole historical world; it is becoming a **small, curator-governed evidence graph** built around `Entity`, `Subject`, `Assertion`, `SourceObservation`, and `Proposal`. That is a much stronger foundation for Chrystallum’s Roman Republic pilot and its larger goal of discovering non-obvious historical connections.

The best decision in the revision is the separation of four things that the legacy design tended to mix:

1. A historical thing.
2. A topic or inquiry about that thing.
3. A proposition connecting things.
4. The evidence and editorial decision supporting that proposition.

The branch also shows healthy implementation discipline: guarded and retry-safe writes, deterministic identifiers, immutable source metadata, passage-level quotation validation, human acceptance before durable knowledge, and tests preventing reusable code from containing Actium-specific assumptions.

The main risk is no longer uncontrolled complexity. The risk is that the current minimal assertion identity—essentially subject, predicate, and object—will be too narrow for the next planned features: temporally qualified relations, attributed narratives, competing interpretations, command capacities, quantitative organizational structures, and source disagreement.
## Repository status
`GraphRevised` is in the public repository but presently appears on the `graph-revised-clean-start` branch rather than the default `master` tree. The public root description still represents the older 5.5-layer/17-agent architecture, so someone arriving through the default README could easily mistake the legacy design for the current direction.[^1]

The revised branch contains a coherent sequence of architecture documents, implementation phases, adapters, proposal code, tests, preserved source payloads, inquiry definitions, review queues, run traces, and Actium-specific seed slices. The current handoff describes a local graph of 4,142 nodes and 4,169 relationships, dominated by 4,025 `Year` nodes, with a deliberately small Actium evidence slice layered on top.

One documentation inconsistency should be corrected immediately: `19-SESSION-HANDOFF.md` says its branch state was not pushed and names an earlier commit, while the handoff itself is publicly present on a later branch revision. The architectural content is useful, but its operational metadata is stale.
## Architectural strengths
### Evidence before automation
The revised architecture correctly makes the graph useful without agents. Direct Cypher operations, deterministic validation, and curator decisions exist before orchestration. This prevents the agent framework from becoming the ontology and supports inspection, testing, replay, and future replacement of individual models.

The rule **“agents propose; curators accept”** is especially sound. It gives Chrystallum an explicit epistemic boundary: generated output is workflow material until reviewed, while accepted assertions form the historical graph.
### Local identity
Chrystallum IDs remain primary, while Wikidata QIDs and other authority identifiers are external records. This supports the project’s preference for Wikidata as a multilingual federation hub without allowing Wikidata’s ontology or changing content to define local identity.

The identity queue is also a good control point. A passage reader can report an unresolved person or group without silently creating a duplicate or selecting the wrong QID.
### Source preservation
The distinction between `AuthorityRecord`, `SourceObservation`, and `Assertion` is excellent:

- An `AuthorityRecord` identifies an external record.
- A `SourceObservation` preserves exactly what was retrieved or read.
- An `Assertion` states what Chrystallum proposes or accepts locally.

Byte-level hashes, source revisions, retrieval dates, statement IDs, passage locators, and raw-payload references make later audit and replay possible. Keeping editorial notes distinct from ancient-source text is particularly important for historical scholarship.
### Bounded vocabulary
The versioned predicate registry prevents an LLM from inventing relationship types or stretching a vague predicate to fit a passage. The planned split between `heldAuthorityOver` and `commanded` is exactly the kind of historically meaningful refinement Chrystallum needs: formal authority and exercised command are not equivalent.

The associated decision to retain source vocabulary such as *imperium*, *triumvir*, *legatus*, or *praefectus classis* rather than imposing modern strategic/operational/tactical categories fits the user’s IGAR objective of reducing presentism.
### Vertical-slice method
Using Actium to exercise entity resolution, subjects, years, external identity, source preservation, assertion creation, proposal review, and evidence tracing is better than rebuilding the old architecture wholesale. The legacy triage categories—adopt, adapt, reference, archive, and exclude—provide a disciplined migration boundary.
## Conceptual issues
### Assertion identity
The current deterministic assertion identifier is built from the predicate and two endpoints. That works for simple claims such as:

```text
Agrippa — participatedIn → Battle of Actium
```

It becomes ambiguous once claims include semantic qualifiers:

```text
Agrippa — commanded → Octavian's fleet
context: Battle of Actium
capacity: praefectus classis
valid time: 31 BCE
according to: Plutarch
```

Two claims with the same endpoints but different time, capacity, event context, modality, or attribution should not necessarily collapse into one assertion. Before implementing registry v3, Chrystallum should choose explicitly between two models:

- **Proposition model:** one assertion represents a canonical proposition; sources and assessments support, oppose, or qualify it.
- **Claim-expression model:** each source-qualified or context-qualified formulation is a distinct assertion.

A practical hybrid is preferable: a canonical `Proposition` identity based on normalized semantic content, plus source-specific `Claim` or `Attribution` records that assert, deny, depict, or qualify it. If the project retains only `Assertion`, its deterministic ID should include a canonical qualifier signature whenever qualifiers change the proposition’s meaning.
### Narrative versus fact
The handoff correctly states that narrative detail is an author’s depiction, not automatically a historical fact. This needs to become a first-class graph rule before micro-events are added.

For example:

```text
Plutarch's Antony
  └─ depicts/asserts
       └─ Cleopatra raised a signal on her ship
```

is different from:

```text
Cleopatra
  └─ performed
       └─ raising a signal
```

The first is directly evidenced by a passage. The second is a historical inference requiring evaluation against other sources. E12 should therefore precede large-scale micro-event extraction.
### Subject semantics
The Entity/Subject distinction is useful, but a `Subject` should not become an automatic shadow node for every `Entity`. That would double the visible graph and reproduce the complexity the refactor is trying to remove.

Treat `Subject` as an intentional research scope, body of literature, inquiry hub, or navigational topic. Create one when it organizes evidence, questions, lenses, or user work—not merely because an entity exists.
### Direct temporal edges
`Entity-[:IN_YEAR]->Year` is useful for navigation, but an evidence graph must define whether that edge is:

- accepted knowledge;
- a materialized projection derived from accepted temporal assertions; or
- an unsourced convenience edge.

The cleanest long-term approach is to make qualified temporal assertions authoritative and materialize `IN_YEAR` as a rebuildable navigation index. Otherwise, a direct year edge can bypass the provenance requirements imposed on other historical facts.

There is also a contract inconsistency to fix: the graph model permits an assertion object to be a `Year`, but the documented canonical endpoint signature lists only `Entity`, `Subject`, and `AuthorityRecord` as possible objects.
### Workflow versus knowledge
The README says agent workflow state should remain outside the semantic core, yet `Proposal` is a durable graph node. This is reconcilable, but the boundary should be stated precisely:

- Submitted/accepted/rejected proposal records may remain as durable editorial audit history.
- Queues, locks, retries, model jobs, checkpoints, and transient orchestration state remain outside Neo4j.
- Ordinary historical exploration hides `Proposal` nodes unless audit mode is requested.

Without this clarification, future contributors may either remove valuable audit records or begin storing an entire job engine in the historical graph.
## Evidence model gaps
### Sources and editions
Passage observations currently preserve edition details largely as properties. That is sufficient for one Perseus text but will become restrictive when comparing translations, editions, manuscripts, ancient works, modern articles, inscriptions, and archaeological reports.

Before the second-source phase, add a minimal source identity model:

```text
Work
└── EditionOrWitness
    └── SourceObservation
```

This need not become a full FRBR or CIDOC implementation. It only needs stable identities for the intellectual work and the particular carrier or edition from which text or data was observed.
### Evidence stance
The graph records that an observation supports an assertion, but historical evidence also contradicts, weakens, contextualizes, mentions, or is irrelevant to a claim. The planned “evidence stance” backlog should become an explicit controlled vocabulary:

```text
supports
contradicts
qualifies
mentions
is_silent_on
```

Silence should be used cautiously and only where a source would reasonably be expected to mention the matter.
### Confidence and assessment
The architecture describes confidence or evidence assessment, but the core `Assertion` contract is principally status-based. Avoid a single undifferentiated numeric confidence property. A curator assessment should record who evaluated the evidence, under what rubric, when, and with what conclusion.

A compact pattern would be:

```text
EvidenceAssessment
- assessedBy
- assessedAt
- stance
- strength
- rationale
- methodVersion
```
## Implementation quality
A focused offline test run completed successfully: 36 prompt-version, identity-adapter, registry, validator, quotation, and proposal tests passed. Live Neo4j tests were not executed in this review because the public branch does not include the local database credentials or running database described by the handoff.

The test design is strong in several respects:

- Prompt versions change when text or template code changes.
- Reusable modules are tested against subject/source hard-coding.
- Missing entities cause failure rather than silent creation.
- Unsupported predicates fail deterministically.
- Passage evidence must quote the preserved passage rather than paraphrase it.
- Editorial notes cannot be quoted as ancient evidence.
- Existing and pending evidence are checked for duplication.

The next tests should target qualifier canonicalization, proposition identity, attribution, supersession links, evidence stance, and temporal overlap.
## Product direction
The Explorer UI direction is appropriately graph-first: central stage, contextual cards, timeline, maps, path tracing, and bridge discovery. The chosen sequence—read API before React/Cytoscape implementation—is correct because it prevents visual components from embedding database semantics.

The read API should expose projection objects rather than raw storage nodes. In ordinary exploration, an accepted `Assertion` can render as an edge while retaining an assertion ID that opens its provenance card. `Proposal`, rejected evidence, and workflow history should appear only in review or audit modes.

Three exploration operations should drive the API contract:

1. **Trace:** show how entity A connects to entity B with provenance.
2. **Expand:** reveal bounded neighbors by time, place, subject, predicate, or source.
3. **Bridge:** reveal modern scholarship, archaeology, or scientific analysis that supports or revises an ancient claim.

The third operation matches Chrystallum’s distinctive goal: modern evidence connected across time to ancient events should be discoverable rather than rejected merely because it crosses periods.[^2]
## Roman Army fit
The Roman Army research is an excellent second architectural stress test, but it should not yet be bulk-loaded. It introduces exactly the structures that reveal whether the revised core can scale without returning to ontology sprawl:

- Unit type versus historical unit instance.
- Nominal establishment versus observed strength.
- Organizational model versus actual containment.
- Commands qualified by time, campaign, office, and capacity.
- Source disagreement and retrospective reconstruction.
- Overlapping manipular and cohortal models.
- Quantities and composition rules.

The current `Entity.kind` categories can represent a historical legion or allied force as `Group`, but they cannot cleanly express reusable types and quantitative composition patterns. Do not immediately add `Legion`, `Cohort`, `Maniple`, and `Century` as Neo4j labels. First test a small domain vocabulary using entities plus controlled typing and assertions:

```text
Historical force instance: Caesar's Legio X in 58 BCE
Unit type: Legion
Organization model: Late-Republican cohortal legion
Composition assertion: normally contains ten cohorts
Strength observation: estimated effective strength at a date
```

If this cannot be represented without distorting `Assertion`, that is concrete justification for a small `StructuredValue` or `CompositionRule` extension. The Roman Army should therefore follow the command/qualifier and attribution work, not precede it.
## Priority order
| Priority | Action | Reason |
|---:|---|---|
| 1 | Finish predicate registry v3 and the command split | Resolves a known semantic conflation before more claims are accepted |
| 2 | Define qualifier canonicalization and assertion identity | Prevents time, capacity, context, and attribution from being collapsed |
| 3 | Implement E12 attribution/depiction | Separates what a source says from what Chrystallum accepts as historical fact |
| 4 | Add supersession links and reason codes | Preserves the evolution of the graph without silent replacement |
| 5 | Complete the held-out passage evaluation | Measures extraction quality after prompt tuning on Actium passages |
| 6 | Implement qualified time as authoritative, with year links as projection | Unblocks offices, marriages, commands, alliances, and unit validity intervals |
| 7 | Add a minimal Work/Edition source model and second adapter | Tests whether provenance generalizes beyond one Perseus source |
| 8 | Build the bounded exploration/read API | Establishes the contract required by path tracing and UI |
| 9 | Use Roman Army organization as the next schema stress test | Tests types, instances, hierarchy, quantities, and scholarly uncertainty |
| 10 | Begin the React/Cytoscape explorer | UI should consume a stable projection API rather than raw Neo4j structure |
| 11 | Add CCA/SCA fan-out only after quality gates pass | Avoids multiplying weak proposals and curator workload |
## Immediate repository changes
The following small changes would make the direction clearer without expanding the ontology:

- Make `graph-revised-clean-start` the visible development branch or add a prominent root README notice linking to `GraphRevised/README.md`.
- Update `19-SESSION-HANDOFF.md` so branch, commit, and push status match GitHub.
- Add an `ADR/` directory for decisions such as proposition identity, authority-versus-command, temporal authority, and proposal retention.
- Add a machine-readable `graph-model-version` and `predicate-registry-version` to read responses and run traces.
- Add CI for offline tests on every push; keep live Neo4j tests as a separate opt-in job.
- Add a small architectural conformance test ensuring every accepted assertion has at least one accepted evidence link unless explicitly marked as curator knowledge with a rationale.
## Final comment
The refactor has changed Chrystallum from an ambitious collection of ontologies and agents into something more defensible: a historical evidence system with controlled federation, explicit provenance, human adjudication, and a graph exploration product on top. That is the correct direction.

The architecture should now resist two temptations: adding the 18 facet agents too early, and treating every domain requirement as a new Neo4j label. The next decisive work is not broader ingestion; it is making the assertion model capable of representing **who says what, about whom, in what context, during what time, with what evidence, and under what interpretation**. Once that contract is stable, Roman military organization, political offices, alliances, places, and cross-temporal evidence bridges can all extend the system without undermining it.

---

## References

1. [GitHub - defarloa1-alt/graph1: Chrystallum project](https://github.com/defarloa1-alt/graph1) - Chrystallum project. Contribute to defarloa1-alt/graph1 development by creating an account on GitHub...

2. [remember that we want to uncover edges not obvious. so if something happened today that might edge to a romaon republic claim that would be gold](https://www.perplexity.ai/search/530f416d-b505-45da-b025-caa4c5594f0d) - Brilliant point! You're right - the real value is discovering non-obvious temporal bridges across ce...

