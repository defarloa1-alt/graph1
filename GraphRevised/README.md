# Chrystallum Graph Revised

## Purpose

This folder is the clean-start design space for Chrystallum.

==The previous model accumulated too many node types, relationship types, agents,==
==authority mappings, and workflow states before the smallest useful graph had==
==been proven==. This revision starts with a smaller contract:

1. represent durable things;
2. represent subjects about those things;
3. represent evidence-bearing assertions;
4. connect dates to the existing temporal backbone;
5. add external authorities only when they help resolve or explain a node;
6. expand the model only when a real use case requires it.

The design in this folder is intentionally more conservative than the legacy
architecture. It is a starting point, not a claim that every future historical
concept has already been modeled.

## Direction and roadmap

Chrystallum is for exploring a network of historical relations and
discovering connections, not an encyclopedia. The agreed roadmap (phases A–F)
is in [docs/Response - Use Cases.md](docs/Response%20-%20Use%20Cases.md); the
product surface is described in [20-EXPLORER-UI.md](20-EXPLORER-UI.md); the
current state and next task are in [19-SESSION-HANDOFF.md](19-SESSION-HANDOFF.md).

## Read in this order

0. [00-NEO4J-SCHEMA-SNAPSHOT.md](00-NEO4J-SCHEMA-SNAPSHOT.md) — read-only baseline of the active local database
1. [01-ARCHITECTURE.md](01-ARCHITECTURE.md) — the small conceptual model
2. [02-GRAPH-MODEL.md](02-GRAPH-MODEL.md) — the initial node and relationship contract
3. [03-TEMPORAL-YEAR-BACKBONE.md](03-TEMPORAL-YEAR-BACKBONE.md) — the temporal structure already present in Neo4j
4. [04-IMPLEMENTATION-PLAN.md](04-IMPLEMENTATION-PLAN.md) — the order in which to build and validate
5. [05-AGENT-BOUNDARIES.md](05-AGENT-BOUNDARIES.md) — the front door, agent roles, and governed write path
6. [06-GRAPH-NAVIGATION.md](06-GRAPH-NAVIGATION.md) — the visual graph navigation and read projection
7. [07-DOMAIN-ADAPTATION.md](07-DOMAIN-ADAPTATION.md) — broad historical inquiries and domain-specific federation
8. [08-SCOPE-AND-INTENT.md](08-SCOPE-AND-INTENT.md) — product boundary and front-door scope classification
9. [09-INDEX-HARVESTING.md](09-INDEX-HARVESTING.md) — machine-readable scholarly indexes and source-led harvesting
10. [10-PHASE-1-SCHEMA.cypher](10-PHASE-1-SCHEMA.cypher) — minimum uniqueness constraints
11. [11-PHASE-1-RESULTS.md](11-PHASE-1-RESULTS.md) — applied schema and validation result
12. [12-PHASE-2-ACTIUM.md](12-PHASE-2-ACTIUM.md) — first direct, evidence-bearing graph slice
13. [13-PHASE-3-DIRECT-OPERATIONS.cypher](13-PHASE-3-DIRECT-OPERATIONS.cypher) — reusable direct reads and idempotent writes
14. [14-PHASE-3-RESULTS.md](14-PHASE-3-RESULTS.md) — Phase 3 implementation and validation status
15. [15-PHASE-4-WIKIDATA-IDENTITY.md](15-PHASE-4-WIKIDATA-IDENTITY.md) — candidate-only Wikidata identity adapter
16. [16-LEGACY-TRIAGE.md](16-LEGACY-TRIAGE.md) — legacy adoption boundary and first-pass register
17. [17-PHASE-5-HANDOFF.md](17-PHASE-5-HANDOFF.md) — verified project state and Phase 5 starting point
18. [18-PHASE-5-PROPOSALS.md](18-PHASE-5-PROPOSALS.md) — ProposalDraft, predicate registry, validator, review workflow
19. [Review of the Chrystallum Subject Backbone Architecture.md](Review%20of%20the%20Chrystallum%20Subject%20Backbone%20Architecture.md) — architectural review and recommendations
20. [docs/](docs) — model/API choice review, use cases, and the agreed responses
21. [19-SESSION-HANDOFF.md](19-SESSION-HANDOFF.md) — **current handoff: start here in a new session**
22. [20-EXPLORER-UI.md](20-EXPLORER-UI.md) — first explorer UI direction (history; the screen now is 26 §1)
23. [21-REVIEW-DELEGATION.md](21-REVIEW-DELEGATION.md) — what Claude may decide when the curator delegates review
24. [22-CLAIM-QUALIFIERS.md](22-CLAIM-QUALIFIERS.md) — claim qualifiers and claim mode
25. [23-NARRATIVE-AND-NOTES.md](23-NARRATIVE-AND-NOTES.md) — depicted events and passages of note
26. [24-PERIODS-AND-TRANSFORMATION.md](24-PERIODS-AND-TRANSFORMATION.md) — periods and transformation
27. [25-LIVES-AND-PLAYGROUND.md](25-LIVES-AND-PLAYGROUND.md) — lives first, and a playground for exploration
28. [26-UI-DATA-CONTRACT.md](26-UI-DATA-CONTRACT.md) — **governing:** what the explorer receives, and the screen (§1)
29. [27-GAZETTEER.md](27-GAZETTEER.md) — the gazetteer, a geographic backbone
30. [28-SUBJECT-BUCKETS.md](28-SUBJECT-BUCKETS.md) — subject buckets
31. [29-EVENT-CENTRED-INQUIRY.md](29-EVENT-CENTRED-INQUIRY.md) — **governing:** event-centred inquiry and Chrystallum's account
32. [30-LOGICAL-MODEL.md](30-LOGICAL-MODEL.md) — logical model (UML), descriptive of the graph as built
33. [31-ONE-COMMAND.md](31-ONE-COMMAND.md) — **governing:** one command, a methodology for any subject
34. [32-RESEARCH-WORKSPACE.md](32-RESEARCH-WORKSPACE.md) — **governing:** the research workspace (notes, overlays, saved paths, status)
35. [33-DECISIONS.md](33-DECISIONS.md) — **governing:** the decision register, and which document governs what
36. [34-ENTITY-SUBTYPE-MIGRATION.cypher](34-ENTITY-SUBTYPE-MIGRATION.cypher) — migrate Entity kinds to subtype labels
37. [35-ENTITY-SUBTYPE-RESULTS.md](35-ENTITY-SUBTYPE-RESULTS.md) — migration results and permanent validation command
38. [validate_ontology.py](validate_ontology.py) — read-only subtype and Year-backbone integrity check
39. [36-DATA-DICTIONARY.md](36-DATA-DICTIONARY.md) — node, property, and relationship reference
40. [37-CANONICAL-EXPORT-REQUIREMENTS.md](37-CANONICAL-EXPORT-REQUIREMENTS.md) — requirements for a future portable export; current snapshots are not backups
41. [39-LENS-SPECIALISTS.md](39-LENS-SPECIALISTS.md) — **draft:** standing lens specialists (lens × scope), their dossiers, what they own, peer review (D-137)
42. [40-LENS-SESSION-HANDOFF.md](40-LENS-SESSION-HANDOFF.md) — handoff of 2026-11-12: event roles, `involvedIn`, the entity review (D-138 to D-140)

## Clean-start rules

- The documents in this folder are the active design for the revised graph.
- Legacy documentation is reference material only until explicitly adopted.
- The new graph should begin with the temporal year backbone and a small number
  of general-purpose node and relationship patterns.
- A proposed feature does not become part of the core model merely because an
  external authority supports it.
- A new node type or relationship requires a concrete query or workflow that
  cannot be expressed clearly with the existing model.
- The graph must remain useful when external services are unavailable.
- The Neo4j database is the durable graph; agent workflow state and raw source
  payloads are separate concerns.
- Agent orchestration is not part of the graph's semantic core.
- No conversational agent writes directly to accepted Neo4j knowledge.
- A domain package may extend vocabulary and routing, but may not silently
  redefine the core claim and provenance model.
- The CCA classifies the user's primary intent before entity resolution.

The source adapters support LacusCurtius named Lives with chapter.section
locators and explicitly bounded Gutenberg sections. Gutenberg section
configuration uses `section: {"start": "<heading id>", "end": "<heading id>",
"label": "<description>"}`; its `1.paragraph` references are local to the
selected section, not classical line numbers. Verify heading boundaries and
rights for each preserved edition before using it.

## Current database context

The local Neo4j `neo4j` database began with only the temporal year backbone
(Phase 0). It now also holds the Battle of Actium slice built in Phases 2–5:
entities, identity links, Wikidata and Plutarch source observations,
assertions, and proposals. Current counts are in
[19-SESSION-HANDOFF.md](19-SESSION-HANDOFF.md). The separate local
`historical` database is empty and is not part of the clean-start plan.

## Inquiry graph-context review

For an agent-led, read-only exploration starting from an existing Subject:

```powershell
python -m GraphRevised.discovery.graph_explorer chr:subject:history-of-battle-of-philippi --output <new-review.json>
```

This sends graph tool results to the configured model provider and can incur
costs; those results can include unpublished graph details or source quotations.
Only run it when that sharing and expense are authorized. It uses the
local MCP connector's bounded read tools, limits model and tool calls, and
saves its complete tool-call results and an **unapproved** model summary. It
does not contact Wikidata or Wikipedia online, change the graph, or
automatically feed its findings to the reader. Review entity identities,
assertion statuses and source leads before any separate inquiry change. The
full graph is available through bounded lookups, not loaded into the prompt.

Before reading an event inquiry, curators can preview the graph context without
calling a model or writing to Neo4j:

```powershell
python -m GraphRevised.discovery.inquiry_graph_review <inquiry.json> --output <new-review.json>
```

The review lists in-scope entities, selected graph assertion IDs and statuses,
groups needing identity review, and direct group participation assertions for
other non-depicted events. It is a preview, not an approval gate or complete
provenance report. Scope can include proposed claims and entities reached
through shared commanders; neither inclusion nor another event's participation
is evidence for the passage or the current event. The source brief and passage
reader receive the same warnings and selected context; the reader log records
it. Existing draft validation and curator review still apply.

After reading, review unresolved names from one or more explicitly selected
reader logs against the local graph without model calls or online searches:

```powershell
python -m GraphRevised.identity.queue local-review <inquiry.json> --run <reader-log.jsonl> --run <another-log.jsonl> --output <new-review.json>
```

The report keeps each source, passage, quotation and reader note, and searches
local labels, short labels and available Wikidata aliases across entity kinds.
Matches, statuses and authority links are leads for a curator, not identity
decisions; absent matches do not prove absence. Results are limited per kind
with counts and truncation reported. It does not update the queue, inquiry or
graph, or add approved candidates to reader scope. Online authority research,
identity decisions and scope changes remain separate actions.

For an explicitly authorized passage-reading run, `--graph-lookup --outputs
claims` enables a separate model-led investigation using the local read-only
MCP connector. The agent can search names, inspect existing entities and
authority links, and select contextually identified candidates for that
passage. It must inspect each selected entity and name it in the target text.
Candidates do not persist as changes to inquiry scope or accepted identities.
Identification reasoning is included in any resulting proposed claim, and the
reader log records the tool calls, results, model and token usage. As with all
reader claims, the passage must provide evidence and a curator reviews the
proposal. Other-event forces are not evidence of participation.

This mode makes up to five additional model calls and eight graph-tool calls
per passage, sends graph and passage content to the configured model provider,
and has **no spending cap**. Model retries are disabled in this mode. It is
opt-in, currently supports claims only, and does not search online authorities
or create missing people. Authorize data sharing and estimate cost before
running it; a call limit is not a billing limit.

The event source planner can use a preserved Wikipedia article via
`--wikipedia-article`, and `--seed-unread` keeps provisional inquiry sources
from being called already read. `--estimated-max-usd` together with explicit
input and output prices per million tokens enables a conservative pre-call
estimate and disables automatic retries. This is not a provider-side spending
cap: token estimates and provider billing may differ. The plan records pricing,
usage, and the estimate; copy availability does not itself verify reuse rights.

## Reasoning-led assertion duplicate review

Prepare a read-only evidence packet without calling a model:

```powershell
python -m GraphRevised.discovery.duplicate_review --assertion <assertion-id> --assertion <another-assertion-id> --prepare-only --output <new-packet.json>
```

Alternatively, `--entity <entity-id>` selects assertions directly connected to
that entity, including unary assertions and assertions in every review status.
The scope must contain 2–8 assertions; if an entity has more, select explicit
IDs. Explicit IDs can compare claims with different endpoints or sources.
This bounded selection is not exhaustive graph-wide duplicate discovery.

The packet retains assertion properties, endpoints, qualifiers, proposal
records, direct supersession links and recorded evidence, including available
source quotations and passage text. Rights-unconfirmed passage and quotation
text is withheld. Inspect the packet and authorize its contents before a model
run; it may contain unpublished graph details or source quotations. For a
separately authorized run, repeat the selection with `--authorize-sharing`
instead of `--prepare-only` and choose a different output file. This sends
the packet to the configured model provider, incurs cost, makes one model call
with retries disabled, and has **no spending cap**. The earlier packet is not
reused: graph data is read again for the model run and may have changed.

The model compares every selected pair and provides a redundant, distinct or
uncertain recommendation, rationale, limitations and evidence references.
References and pair coverage are checked, but semantic conclusions are not
automatically verified. Reports are unapproved curator aids, never graph
writes, merges, rejections or supersessions. Existing output files are not
overwritten; model failures and incomplete responses produce no report.

## Actium evidence review

Generate a read-only JSON report of the Actium inquiry's source-specific events,
passage mentions, phases and relevant temporal, causal, placement and identity
assertions:

```powershell
python -m GraphRevised.discovery.actium_evidence_report --output path\to\new-report.json
```

The report uses the local database settings and does not overwrite existing
files. It includes statuses, passage locators and both accepted support and
proposal evidence (distinguished by `evidenceState` and proposal status).
Its source-work scope is not a claim that every event belongs to Actium.
Lexical cross-source candidates are bounded leads, not identity or chronology
assertions; compare their event mentions and evidence before deciding. Phase
placement does not imply date or order. The report may contain private
annotation identifiers, so store and share it accordingly.

## Actium Subject assertion view

For another event with an existing inquiry and Subject-to-focus link, use:

```powershell
New-Item -ItemType Directory -Force GraphRevised\explorer\snapshots
python -m GraphRevised.discovery.event_subject_view GraphRevised\inquiries\your-inquiry.json --output GraphRevised\explorer\snapshots\event-view-new.json
```

The inquiry must name `subjectId`, `narrativeEventId`, and at least one source.
The generator is read-only and refuses to overwrite an existing file. Topical
placements are excluded unless `--section-id` names one existing direct child
Subject; its explicit placements then appear without implying `partOf`.
The view is bounded, not a backup or an assertion that the inquiry is complete.
It does not create an inquiry, Subject, source or graph data.

Generate a read-only JSON view of assertions related to the Actium Subject:

```powershell
New-Item -ItemType Directory -Force GraphRevised\explorer\snapshots
python -m GraphRevised.discovery.actium_subject_view --output GraphRevised\explorer\snapshots\actium-view-new.json
```

Explorer snapshots are local, git-ignored files under
`GraphRevised\explorer\snapshots`; open the chosen JSON in the explorer and use
a new filename for each refresh. They may contain unpublished graph data.

The view requires the Subject's existing focus link. It includes assertions
directly referencing the focus and those referencing events placed through a
`partOf` assertion, including two-hop paths through Actium phases. Every route
lists its events, placement assertions, statuses and evidence; broader Subject
paths and their node statuses are also shown (up to eight hierarchy links).
When present, the Meaning and memory pilot's topical `IN_SUBJECT` placements
are shown separately with their status and referenced source assertion and
evidence; they do not imply historical event membership.
Proposed and accepted assertions remain distinct, and proposal evidence retains
its proposal status. Rejected and superseded assertions are excluded. This is
a bounded relevance view, not an accepted membership or historical fact:
placements may be proposed or mistaken, and no membership is transferred
through people, places, source identity matches, or narrative order. Other
topical placements and other paths are not included. It neither writes to Neo4j
nor overwrites an existing output file.

Newly generated snapshots also include source-specific timeline data for
depicted events reached by this view. The explorer shows source-attributed
`occurred` and `happenedBefore` claims and explicit `depictsSameAs` assertions;
proposed claims remain labeled, and dates are not transferred across sources.
Source-work identification does not itself establish battle membership.
Snapshots include recorded supporting quotations and deduplicated preserved
passage text where the recorded rights match supported public-domain or open
licenses, with edition, rights, and locator metadata. Other text is withheld.
Public-domain statements may be jurisdiction-specific. Source mentions are
not automatically evidence for a particular claim.

### Meaning and memory pilot

The curator chose a child Subject for this history section, piloted before
the other sections. Preview the existing phase and its placement candidates:

```powershell
python -m GraphRevised.discovery.actium_meaning_memory_pilot --output path\to\new-pilot.json
```

The inventory carries the current phase-to-battle assertion and evidence and
the individual proposed placements and their evidence. They are review leads,
not approved Subject memberships. The inventory does not create the child
Subject, replace or retract any assertion. The other phase records are
unaffected. Output files are not overwritten.

The pilot placement tool uses a direct `(Entity)-[:IN_SUBJECT]->(Subject)`
relationship for topical relevance, never event `partOf`. It takes an explicit
manifest of individual depicted events, each with a reason and its existing
phase-placement assertion ID; it checks that the original assertion is live
and has observed evidence. New placements are **proposed**, even when the
curator chooses them for submission. They retain the original assertion ID
for evidence lookup, plus the proposer and timestamp. Decisions on each
placement record the reviewer, time and basis; accepted or rejected decisions
are terminal in this pilot. Rejecting a placement does not reject the event,
its source, or its historical claims.

Example manifest (replace the IDs with selected entries from the inventory):

```json
{
  "curator": "TD",
  "placements": [
    {
      "eventId": "chr:entity:depicted:example:event",
      "sourceAssertionId": "chr:assertion:example",
      "reason": "The source depicts commemoration of the battle."
    }
  ]
}
```

```powershell
python -m GraphRevised.discovery.meaning_memory_placements submit path\to\manifest.json
python -m GraphRevised.discovery.meaning_memory_placements decide chr:entity:depicted:example:event --decision accepted --by TD --basis "Reviewed the source and topical relevance."
```

Both commands default to offline preview. `--apply` explicitly writes to local
Neo4j: submit creates the candidate child Subject, its `NARROWER_THAN` link,
and only the listed proposed placements atomically; decide changes exactly one
proposed placement. The table shows proposed and accepted placements after a
fresh view is generated; rejected placements stay in the graph for review but
are excluded from the exploration view. No command here retires the accepted
phase-to-battle assertion or modifies individual old `partOf` claims; their
review and any retraction require a separate curator decision. Until then,
legacy routes remain visible and should not be read as establishing that
aftermath events were part of the fighting.
