---
status: informational
authority: none; decisions remain in 33-DECISIONS.md
last_reviewed: 2026-11-11
---

# Session handoff: reasoning-led graph review

## Start here

The curator wants agents to reason about historical meaning and existing graph
structure. Deterministic matching and validation are useful for finding and
checking leads, not for deciding identity, equivalence, causality or truth.
Preserve source voices, evidence, uncertainty and review history. Do not
silently merge, delete, supersede or accept claims.

**Next unfinished feature:** agree with the curator on a broader,
reasoning-led passage review. The existing reader already supports depicted
events, relationships and unresolved mentions, but the desired integrated
review of coverage, graph connections, open questions and overstatement is
not yet complete. Do not describe it as delivered.

First inspect [passage_reader.py](proposals/passage_reader.py), especially
the reader prompt, depicted-event handling and validation, together with
[passage_graph_lookup.py](discovery/passage_graph_lookup.py) and the existing
review interfaces. Confirm the output contract and whether review remains
read-only or may later submit proposals before implementing. Use Antony 68.3
below as a regression case; do not make a paid call without a new, explicit
authorization covering scope, provider sharing and estimated budget.

## Current working features

- **Assertion duplicate review:** [duplicate_review.py](discovery/duplicate_review.py)
  prepares a read-only evidence packet for 2-8 explicit assertions or a bounded
  entity neighborhood. A model can compare every selected pair and recommend
  redundant, distinct or uncertain, with reasons, limitations and checked
  evidence references. Selection is not exhaustive graph-wide discovery;
  conclusions are unapproved. It does not write to the graph. The command,
  model-sharing warning and limits are in [README.md](README.md).
- **Passage identity lookup:** the opt-in `--graph-lookup --outputs claims`
  reader mode uses bounded local read-only MCP tools to inspect candidate
  identities per passage. Selected identities are temporary and can support
  proposed, not accepted, claims; reasoning and calls are logged. It is not a
  complete passage-reasoning workflow or an online authority search.
- **Local identity review:** `identity.queue local-review` reports local
  candidates from explicitly selected reader logs without model calls or
  graph writes.
- **Registry v12:** Work-to-Work `partOf` is permitted; D-136 in
  [33-DECISIONS.md](33-DECISIONS.md) governs. No Brutus-to-collection claim
  was created merely by this change.

Both model-enabled review paths have **no built-in spending cap**. The paid
pilots used separate session-only wrappers with pre-call estimates and retries
disabled; a token/call limit or estimate is not a provider-side billing cap.
The duplicate-review CLI rereads the graph for its model run, rather than
reusing a previously inspected packet; data can change between the two.

## Worked passage: Plutarch, Antony 68.3

The source passage says Antony's soldiers held together for seven days and
paid no heed to Caesar's messages. After Canidius had fled the camp by night,
and with the soldiers destitute and betrayed by commanders, they went over
to the conqueror. The passage **does not say what Caesar's messages contained**.
That is a research question, not a fact to invent.

The live graph was read on 2026-11-11:

- Provisional Person `chr:entity:publius-canidius-crassus` exists. Accepted
  `commanded` and `heldAuthorityOver` assertions connect him to Antony's land
  army and are supported by this observation.
- Proposed source-depicted Event
  `chr:entity:depicted:plutarch-life-of-antony:canidius-flees-the-camp-by-night`
  exists; a proposed `participatedIn` assertion connects Canidius to it.
  Proposed events also represent the seven-day holdout and the army going
  over to Octavian.
- A proposed `happenedBefore` assertion orders the holdout before Canidius's
  flight, and a proposed `triggeredBy` assertion links his flight to the
  army's going over. Review these carefully: the text places the going over
  after his departure and mentions multiple circumstances; sequence alone
  does not prove a precise boundary or a sole cause.
- Three flagged entity-mention annotations link the observation to those
  depicted events. In the assertions linked to this passage, no claim about
  Caesar's messages was found; a bounded label search for related
  Caesar/Octavian message events also returned no match. That search does
  not prove graph-wide absence.

Regression expectations for the proposed broader review: preserve actor,
event, source and status; recognize existing graph matches; identify the
messages and soldiers' response as potential source-supported leads; leave
message content unknown; distinguish textual sequence from supported causal
claims; identify missing or disputed connections with evidence and uncertainty.
These are examples, not rules replacing the agent's reasoning.

## Duplicate finding and review boundaries

The Plutarch holdout has two proposed `occurred` assertions, with time source
expressions `seven days` and `for seven days`, each with a separate submitted
proposal and the same observation
`chr:observation:perseus:tlg0007.tlg058.perseus-eng2:68.3:70427323`.
The 2026-11-11 paid model review recommended **redundant**, not independent
corroboration; this is not a curator decision. Both qualifier quotations
cite the same clause. The model noted registry v10 versus v11; a subsequent
local check found their `occurred` definitions identical.

`qualifier_signature` in [registry.py](proposals/registry.py) incorporates
the exact unnormalized time expression in assertion IDs. Do not normalize
IDs or merge the pair without an authorized migration and evidence/review
history policy. The timeline displays separate assertions, hence two rows.

Prior live-graph investigation identified 38 same-endpoint/mode/Work candidate
groups containing 84 assertions (including unary claims), 24 with a shared
observation. These are leads, not confirmed duplicates. Eleven same-label,
same-kind entity groups had distinct accepted Wikidata IDs; several are real
namesakes. Do not merge on a label, shared observation or matching endpoints.
The explorer's previously loaded Actium snapshot was not located on disk, so
do not equate its counts with the live graph.

## Philippi state and pilots

- The candidate Subject `chr:subject:history-of-battle-of-philippi` is linked
  to the existing proposed Event `chr:entity:battle-of-philippi`. Five missing
  Work records were created as proposed after curator approval; an eight-work
  inquiry draft is session-only and review-only.
- Six new edition payloads and sidecars are under
  [phase-9-source](phase-9-source); they are uncommitted. Existing Augustus
  and Velleius editions were reused. Preserve recorded attribution and
  licensing; rights may vary by jurisdiction.
- First paid pilot: Appian 4.13.105 and Plutarch Brutus 38.4 and 53.3,
  estimated $0.195172; no claim drafts, so no claims or observations stored.
  A subsequent MCP-enabled Brutus 38.4 pilot identified Octavius as existing
  Augustus and Mark Antony; Brutus and Cassius remained unresolved. Across
  its four attempts, estimated cost was $0.364040; no claim drafts or passage
  observation were stored.
- A separate paid duplicate review of the seven-day pair estimated $0.03572
  using conservative $4/million input and $20/million output rates; actual
  provider billing may differ. The $2 authorization was specific to that
  pair and did not authorize a wider audit.

Do not treat graph context as evidence for another passage or infer that
Actium-specific forces participated at Philippi merely because of a shared
commander. The Philippi source-only backup at
`C:\graph1Revised\backup\philippi-sources-20261111T123347Z` was hash-verified;
it is **not a Neo4j backup**.

## Validation and operational state

- On 2026-11-11,
  `python -m pytest GraphRevised\tests\test_duplicate_review.py GraphRevised\tests\test_actium_evidence_report.py GraphRevised\tests\test_graph_explorer.py -q`
  passed: **21 tests**. A live read-only packet check verified both seven-day
  assertions, their distinct qualifiers and proposals, shared observation and
  quotations. The actual paid output is a model recommendation, not a
  ground-truth test of reasoning quality.
- Earlier focused passage graph-lookup and offline-reader tests passed:
  **22 tests**. Registry tests passed **73**, with **4 skipped**; other
  previously run source/reader tests passed **43**. Re-run relevant checks
  after changes rather than assuming these historic results still hold.
- Snapshot inventory from 2026-11-11: 516,909 nodes, 519,207 Neo4j
  relationships; 707 Entities and 2,187 Assertions. It is a historical
  read-only snapshot, not a current guarantee. Neo4j is the operational
  authority; explorer exports are not backups.
- Branch at handoff: `graph-revised-clean-start`. The worktree is extensively
  dirty, including work from before this session and untracked source files.
  Nothing from this session was committed. Inspect and preserve all existing
  changes; do not reset or stage the entire worktree blindly. Review what
  belongs together before any user-authorized commit. Plan and verify a
  separate graph backup before destructive graph operations.

## Session-only artifacts

These are outside the repository and may not be available in another
environment. They are not commits or backups. Inspect before moving or sharing,
because packets may contain graph details and source quotations.

Under
`C:\Users\defar\.copilot\session-state\ce7bad2d-54f9-419d-b09d-16b6fcd775c1\files`:

- `seven-day-paid-review.json`, `seven-day-paid-review-budget.jsonl` and
  `duplicate-review-packet-verified.json`: review, estimated cost and input.
- `actium-duplicate-review.md`, `actium-duplicate-evidence.json` and
  `actium-duplicate-investigation.json`: duplicate candidates and evidence.
- `philippi-inquiry-eight-sources-draft.json`, `philippi-pilot-scope-review.md`,
  `philippi-pilot-local-identity-review.json`,
  `philippi-approved-source-check.md` and `philippi-work-records-review.md`.
- `philippi-mcp-pilot-budget*.jsonl`, `philippi-pilot-budget.jsonl` and
  `graph-inventory-20261111.json`: run estimates and graph inventory.

Successful paid Philippi reader log:
`GraphRevised\runs\philippi-mcp-pilot-fourth-20261111\passage-reader-20261111T145316Z.jsonl`.
Before any reuse, confirm the file and graph are still available and current.
