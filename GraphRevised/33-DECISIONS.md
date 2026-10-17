---
status: governing
authority: the record of decisions, and which document governs what
depends_on: []
superseded_by: null
last_reviewed: 2026-10-17
---

# 33 — Decisions

**Date:** 2026-10-17. **From:** the sequence-diagram review
([docs/Sequence Diagram.md](docs/Sequence%20Diagram.md)), handoff next step 1f2
(a) and (f).

One line per decision: what was decided, when, by whom, and where the
reasoning is. The reasoning stays in the document named; this register is the
lookup, so a decision can be found without reading the history. A decision
that changes is not edited: it is marked superseded and the new one names it.

## 1. Which document governs what (D-001)

Reading order and authority are different things. The handoff is read first
and governs nothing but the decisions it records, which belong here.

| Question | Governs |
|---|---|
| What a thing means and how it is stored: labels, kinds, relationships, statuses, identity | [02](02-GRAPH-MODEL.md) |
| What the agents do: which runs, in what order, with what plan, review, and stopping | [31](31-ONE-COMMAND.md) |
| How an event inquiry specializes 31 | [29](29-EVENT-CENTRED-INQUIRY.md) |
| The curator's workspace: plans, notes, overlays, saved paths, status display | [32](32-RESEARCH-WORKSPACE.md) |
| What the explorer receives | [26](26-UI-DATA-CONTRACT.md) |

Then, in order: the code and its data files, which must conform; the handoff
([19](19-SESSION-HANDOFF.md)); the inputs in `docs/`, which inform and never
govern. [30](30-LOGICAL-MODEL.md) describes the graph as built: where it and
02 disagree, 02 governs and 30 is out of date.

- 02 and 31 have no order between them: a question of meaning goes to 02, a
  question of behaviour to 31.
- 29, 32, and 26 may add to 02 and 31 but not contradict them; a
  contradiction needs a decision here first.
- A decision recorded here and a governing document that disagrees with it:
  the document is out of date and is brought in line.
- The numbered documents not in the table (00–18, 20–25, 27, 28) are history:
  the reasoning behind decisions. What they decided is in 02 or here; where
  they disagree with a governing document, the governing document wins.
- Governing documents carry front matter: `status`, `authority`,
  `depends_on`, `superseded_by`, `last_reviewed`.

## 2. The register

`By`: the curator (Tony DeFarlo), unless marked. Status: in force unless
marked.

### 2026-10-11 to 2026-10-12

| ID | Decision | Recorded in |
|---|---|---|
| D-010 | A clean start on the local Neo4j database: a few core labels, legacy material reference only | README, [16](16-LEGACY-TRIAGE.md) |
| D-011 | Agents propose; a deterministic validator checks; only the curator accepts | [05](05-AGENT-BOUNDARIES.md), [18](18-PHASE-5-PROPOSALS.md) |
| D-012 | The agent runtime is the Anthropic SDK; the source-discovery research API waits (E9) | [docs/Response - Model and API Choice.md](docs/Response%20-%20Model%20and%20API%20Choice.md) |
| D-013 | The product is a custom React and Cytoscape.js explorer designed in Figma; Neo4j Bloom is for smoke tests only | [20](20-EXPLORER-UI.md) |
| D-014 | Evidence and claim are decided separately: rejecting evidence leaves the claim open | [18](18-PHASE-5-PROPOSALS.md) §15 |
| D-015 | `commanded` (command exercised) split from `heldAuthorityOver` (authority held); reason codes on every rejection; supersession and retraction | [18](18-PHASE-5-PROPOSALS.md) §17 |
| D-016 | Delegated review is limited to what a verbatim quotation lets anyone check, and is signed as delegated | [21](21-REVIEW-DELEGATION.md) |
| D-017 | Qualifiers (time, role, context, attribution) are part of a claim's identity; claims are asserted or attributed; the reader's default is attributed | [22](22-CLAIM-QUALIFIERS.md) §3, §4, §12 |
| D-018 | An expected qualifier is a note, not a gate: an undated claim is stored and marked UNDATED; a unary claim still needs its time | [22](22-CLAIM-QUALIFIERS.md) §7 |
| D-019 | Readers locate passages themselves: inquiries name whole works, guidance carries no locators | [18](18-PHASE-5-PROPOSALS.md) §20 |
| D-020 | Depicted events (one source's narrative units, proposed by the reader) and passages of note (Annotations, never claims) | [23](23-NARRATIVE-AND-NOTES.md) §9 |
| D-021 | Interpretive claims are attributed only (`exemplifies`, `ledTo`); kinds Office and Concept | [23](23-NARRATIVE-AND-NOTES.md) §6, §9 |
| D-022 | Periods are discovered, never seeded; a period's dates are claims; membership in a period is computed, never stored | [24](24-PERIODS-AND-TRANSFORMATION.md) §8 |

### 2026-10-13

| ID | Decision | Recorded in |
|---|---|---|
| D-030 | People first, facets after: lives are the backbone, facets become lenses on it | [25](25-LIVES-AND-PLAYGROUND.md) §2 |
| D-031 | Everything is visible at once, labelled with status and source; the curator promotes rather than gates | [25](25-LIVES-AND-PLAYGROUND.md) §2 |
| D-032 | Imaginative is a third category, derived from the attributed Work's form, never chosen; fiction never supports an asserted claim | [25](25-LIVES-AND-PLAYGROUND.md) §6 item 3 |
| D-033 | Attestation is computed at read time, in words, from distinct authors; never a stored score | [25](25-LIVES-AND-PLAYGROUND.md) §6 item 4 |
| D-034 | Quiet provenance: voices ("according to Plutarch") are content, source systems stay in the sidebar | [25](25-LIVES-AND-PLAYGROUND.md) §5 |
| D-035 | Never display a code alone; check every identifier at its authority; LCC is not used | [25](25-LIVES-AND-PLAYGROUND.md) §8 |
| D-036 | Four kinds of Wikidata statement (identifier, attribute, relationship, housekeeping); every date tethers to the Year backbone | [25](25-LIVES-AND-PLAYGROUND.md) §10 |
| D-037 | The one-hop rule: any agent proposes the people, places, events, offices, groups, and periods it meets, within a budget | [25](25-LIVES-AND-PLAYGROUND.md) §11 |
| D-038 | The actors, in chronological order, Hannibal first; agents choose the sources; data is not in git | [25](25-LIVES-AND-PLAYGROUND.md) §13 |
| D-039 | Kinds Type and Polity; powers (*imperium*) are Types; facets are lenses, not nodes; canonical trees are views, never stored | [Institutions response](docs/Response%20-%20Roman%20Republican%20Institutions%20and%20Military%20Hierarchies.md) |
| D-040 | The Roman Republic, Kingdom, and Empire are Polities; a period the reader names stays a Period | [24](24-PERIODS-AND-TRANSFORMATION.md) §2 |
| D-041 | PeriodO gives definitions, Wikidata gives identity; both kept | [24](24-PERIODS-AND-TRANSFORMATION.md) §9 |
| D-042 | Only facts that happen once (registry `once`) are disputed by differing times, contexts, or roles | [19](19-SESSION-HANDOFF.md) §5 |
| D-043 | `opposed`: one symmetric predicate with time, no Wikidata mapping | [25](25-LIVES-AND-PLAYGROUND.md) §6 item 1 |

### 2026-10-14

| ID | Decision | Recorded in |
|---|---|---|
| D-050 | The SCA and SFA are retired; their ideas survive as rules for the harvest and enrichers by kind | [25](25-LIVES-AND-PLAYGROUND.md) §11 |
| D-051 | One authority record per system and identifier | migration 007; [19](19-SESSION-HANDOFF.md) §3 |
| D-052 | The geographic backbone first: a Location layer from Pleiades and the GeoNames administrative tree, TGN as identifiers only | [27](27-GAZETTEER.md) §1 |
| D-053 | Every entity in a subject bucket: our own hierarchy anchored to LCSH and FAST, membership computed from claims, P921 not used | [28](28-SUBJECT-BUCKETS.md) |

### 2026-10-15

| ID | Decision | Recorded in |
|---|---|---|
| D-060 | The event is the inquiry, not a Work. **Superseded by D-088** (the wording; the substance, an inquiry names an event rather than a Work, stands) | [29](29-EVENT-CENTRED-INQUIRY.md) §2 item 1 |
| D-061 | Chrystallum's account sits beside the event, labelled as ours, every statement citing a preserved passage; never counted as an author | [29](29-EVENT-CENTRED-INQUIRY.md) §2, §4 |
| D-062 | Wikipedia: a starting point for discovery, a link on the card, and a labelled tertiary voice | [29](29-EVENT-CENTRED-INQUIRY.md) §5 |
| D-063 | Facets are lens steps in the drill-down path | [29](29-EVENT-CENTRED-INQUIRY.md) §2 item 4 |
| D-064 | The source registry is a starting point, not a whitelist; discovery is not acceptance | [29](29-EVENT-CENTRED-INQUIRY.md) §6 |
| D-065 | Agents prepare the inquiry: the curator writes no guidance, source list, or scope | [29](29-EVENT-CENTRED-INQUIRY.md) §7 |
| D-066 | Event order through `happenedBefore`, apart from the dated cursus order `precedes` | [19](19-SESSION-HANDOFF.md) §5 |
| D-067 | The account is stored, versioned, and introductory, its names linked to the graph | [29](29-EVENT-CENTRED-INQUIRY.md) §4a |
| D-068 | The curator's notes live in the Obsidian vault, the graph holding a link to each (option c) | [29](29-EVENT-CENTRED-INQUIRY.md) §10 item 6 |
| D-069 | A notes stage beside the facts stage | [26](26-UI-DATA-CONTRACT.md) §4a |

### 2026-10-16

| ID | Decision | Recorded in |
|---|---|---|
| D-070 | The battle's phases are our own asserted sub-events, approved by the curator; each source's depicted events are `partOf` a phase | [29](29-EVENT-CENTRED-INQUIRY.md) §10 item 2 |
| D-071 | One stored account per event; persona retellings later, generated from it | [29](29-EVENT-CENTRED-INQUIRY.md) §4a |
| D-072 | One command for any subject: front door, orientation, line-item plan, orchestrator, readers and lenses, reconciler, critic; determinism around agents | [31](31-ONE-COMMAND.md) |

### 2026-10-17

| ID | Decision | Recorded in |
|---|---|---|
| D-080 | The user is the curator, for now | [32](32-RESEARCH-WORKSPACE.md) §1 item 1 |
| D-081 | Line-item plans with approve all; a run stops only for identity, scope, rights, destructive reconciliation, or budget (settles 31 §7 item 1) | [32](32-RESEARCH-WORKSPACE.md) §1 item 2 |
| D-082 | Four content layers; notes are research objects attachable to any object, never claims | [32](32-RESEARCH-WORKSPACE.md) §1 items 3-4 |
| D-083 | Obsidian is an editing client, not the authority | [32](32-RESEARCH-WORKSPACE.md) §1 item 5 |
| D-084 | A core pack and private or shared overlays, composed at read time; promotion from an overlay is a transformation | [32](32-RESEARCH-WORKSPACE.md) §1 items 6-7 |
| D-085 | Saved paths are research objects that assert nothing | [32](32-RESEARCH-WORKSPACE.md) §1 item 8 |
| D-086 | Proposed claims in the same projection as approved ones; path tracing approved-only by default; status shown redundantly (settles 31 §7 item 2) | [32](32-RESEARCH-WORKSPACE.md) §1 items 9-11 |
| D-087 | Match before storing: a candidate is compared with approved and proposed claim families | [32](32-RESEARCH-WORKSPACE.md) §1 item 12 |
| D-001 | Which document governs what (§1) | here |
| D-088 | An inquiry focuses on an entity of any kind (an event, a person, a place, an object, a group, an office, a period; curator, 2026-10-17); it is not that entity. Several inquiries may share a focus, one inquiry may have several. Supersedes D-060's wording. Reason: the event is what happened, the inquiry a research activity with its own scope, plans, and runs (sequence-diagram review). Alternative turned down: one object for both | [29](29-EVENT-CENTRED-INQUIRY.md) §2 item 1; [31](31-ONE-COMMAND.md) §3.11 |
| D-089 | Program, Inquiry, Plan, Run, and Orientation dossier are distinct contracts, and workers hand on evidence packets; all are run state, never graph data. The dossier follows 31 §7 item 4's recommendation, still open to veto. Code: `orchestration/contracts.py` (`inquiry-run-v2`) | [31](31-ONE-COMMAND.md) §3.11, §6 |
| D-090 | The account is traced statement by statement: each is a source statement (preserved passages, verbatim, and the claims it restates), a synthesis (ours, resting on earlier statements, citing nothing itself), or a signpost; sections name their phases; the account is checked against the graph before it is shown. Reason: the account must not become a second, unaudited layer of truth (sequence-diagram review). Alternatives turned down: citing claims only (would drop passages no claim was drawn from, which 29 §4 allows); a synthesis citing passages directly (would blur ours with the sources'). Code: `narrative/account.py` | [29](29-EVENT-CENTRED-INQUIRY.md) §4b; [26](26-UI-DATA-CONTRACT.md) §5 |
| D-091 | The battle's 11 phases approved (curator, 2026-10-17; their `partOf` claims accepted, the phase Entities provisional). Their order is the curator's decision, kept as the ordered spine in `curation/phases.json`, not as `happenedBefore` claims. Reason: the sources order only 5 of the 10 steps, and 4 of their orderings run against the spine. Alternatives turned down: claims for the 5 evidenced steps (the order in two places); all 10 on the curator's authority (a claim without a passage). Source orderings against the spine are a review list (`views/review-status.cypher` query 6). Replaces handoff 1f2(e) | [02](02-GRAPH-MODEL.md) §2; [29](29-EVENT-CENTRED-INQUIRY.md) §9a |
| D-092 | The Obsidian sync: a program outside Obsidian that makes the graph match the notes in one folder, one way (vault to graph), run by a watcher; the folder is `GraphRevised/obsidian_book_notes/`, git-ignored (private notes quoting books in copyright, public repository). It writes transcriptions and Annotations, never claims; it changes a file only to write a new note's id (and, by D-093, the book's id once found). Reason: Obsidian is the editor, the graph the authority (32 decision 5). Alternatives turned down: both ways from the start; a command run by hand. Settles 32 §3 item 3. Not built | [32](32-RESEARCH-WORKSPACE.md) §2.1a |
| D-093 | A note need not find its book in the graph (curator, 2026-10-17): it names the book by `book`, `author`, and optionally `isbn`; `work` is optional. The sync finds the book (ISBN, then title and author) and writes its id into `work`, asks when more than one matches, and otherwise proposes the Work (and its author as a Person), the authorship claim drafted from a catalogue record, never from the note's typed words; the transcription and note are stored at once. The catalogue for modern books is still to be chosen and registered. Reason: notes are written while reading, before anyone adds the book. Alternative turned down: a book must be in the graph first (it would hold up the notes) | [32](32-RESEARCH-WORKSPACE.md) §2.1a |
| D-002 | A decision register (this file). Reverses the earlier recommendation not to keep ADRs ([direction-review response](docs/Response%20-%20Review%20of%20the%20GraphRevised%20Direction.md)): decisions had spread over too many documents to find | here |

## 3. Open

Recorded where they are, not here, until decided: [31](31-ONE-COMMAND.md) §7
items 3-12; [32](32-RESEARCH-WORKSPACE.md) §3; [19](19-SESSION-HANDOFF.md) §5
"Open". When one is decided it gets an entry here.

## 4. A new entry

From D-001 on, a decision made in a session gets an entry with: the decision;
the date and who decided; the reason, in a sentence; the alternatives turned
down; the documents and code it changes. Long reasoning stays in its document;
the entry points to it.
