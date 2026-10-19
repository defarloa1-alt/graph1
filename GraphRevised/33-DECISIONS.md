---
status: governing
authority: the record of decisions, and which document governs what
depends_on: []
superseded_by: null
last_reviewed: 2026-10-19
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
| What the explorer receives, and the screen it is shown on | [26](26-UI-DATA-CONTRACT.md) |

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
| D-035 | Never display a code alone; check every identifier at its authority; LCC is not used (**narrowed by D-094**: not as a hierarchy, but a book's own call numbers are kept) | [25](25-LIVES-AND-PLAYGROUND.md) §8 |
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
| D-094 | The Library of Congress catalog is the catalogue for books (curator: "key"), registered as `loc-catalog`: a book's record found by ISBN, LCCN, or subject heading and preserved byte for byte. LC states no licence for its catalog records; the curator decided that preserving and citing them is **research use**, never republication (the records are git-ignored), to be revisited if LC states one. A book's LCC and DDC numbers are kept as identifiers read from its record, never as a hierarchy (narrows D-035). A publisher's summary in a record is never the author's words. Code: `adapters/lc_catalog.py`, `harvest/lc_record.py` (a record into proposals: `authorOf`, `describedBy` by matching LC ids an Entity holds, the LCCN with call numbers) | `curation/sources.json` (`loc-catalog`); [32](32-RESEARCH-WORKSPACE.md) §2.1a |
| D-095 | Only what the curator alone knows goes in a note: the ISBN of the copy in hand, page or location, optional `chapter`, `quoting` (whose words, when not the author's), `concerns`, `related`, `tags`, and the curator's text; whatever a catalogue gives comes from the record, never typed. `book`, `author`, `edition` only without an ISBN. Claims are not drafted from a `quoting` passage as the author's reading; they wait for the curator until nested attribution exists. Reason: a typed copy of a looked-up fact can only drift from it. Refines D-093 | [32](32-RESEARCH-WORKSPACE.md) §2.1a |
| D-096 | Images the curator gathers: one note per image (`chrystallum: image`), the file in `images/` or a URL; a URL image kept as a private, hashed copy with its URL and fetch date (curator, 2026-10-18); images never in Neo4j, only their records; an image is a depiction and a reconstruction says so. Templates in `_templates/`, skipped by the sync. Open: images as evidence (32 §3 item 4) | [32](32-RESEARCH-WORKSPACE.md) §2.1b |
| D-097 | The sync's check and apply built without the watcher (`capture/notes.py`), with a schema addition the curator approved: an `image` kind of SourceObservation (never evidence) and Annotation kinds `note` and `image-note`. The Campsite Memorial of Augustus proposed as a Place (Wikidata Q132975955). First notes applied 2026-10-18 | [02](02-GRAPH-MODEL.md) §2; [32](32-RESEARCH-WORKSPACE.md) §2.1a |
| D-098 | An ellipsis in the curator's quote block marks words skipped; a claim may not quote across it (the validator refuses such a quotation from a transcription; in a source's own text an ellipsis is the author's and is quoted as such) | [32](32-RESEARCH-WORKSPACE.md) §2.1a; `proposals/validator.py` |
| D-099 | Direct lookup ("vertex jump"): every read and write starts from a node found by a unique, indexed key (the local ids, `Year.year`, `AuthorityRecord.(system, identifier)`), then walks a bounded number of relationships; external codes are found through their AuthorityRecord, never kept inside local ids; claim ids are content-addressed. The legacy three-tier cipher was reviewed (2026-10-18): its claim cipher survives as the claim id; its QID-based entity ids, BabelNet and synthetic cascade, and `FacetedEntity` hubs with stored confidence are dropped. Recorded at the curator's request | [02](02-GRAPH-MODEL.md) §6.1 |
| D-100 | An MCP connector for the local graph (curator, 2026-10-18): read-only first, seven typed lookups (entities by name or authority code, an entity's card, a fact's voices, an event's overview, the review queue, graph status), no Cypher tool (05 §7). Facts come from the exploration projection (26). Reached from Claude Code over stdio (`.mcp.json`) and from claude.ai over HTTP through a Cloudflare quick tunnel, the access token in the path (claude.ai sends no key to a custom connector). Replaces the legacy Railway connector (D-034, Aura, general read-only Cypher), which can't reach a local database. Alternatives turned down: Claude Code only; proposal submission in the first version; ngrok or a named tunnel (a stable URL, but an account or a domain). With it, `battle-overview.cypher` query 5 now counts the passages behind phase placements, which its earlier pattern left out | [05](05-AGENT-BOUNDARIES.md) §7; `connector/` |
| D-002 | A decision register (this file). Reverses the earlier recommendation not to keep ADRs ([direction-review response](docs/Response%20-%20Review%20of%20the%20GraphRevised%20Direction.md)): decisions had spread over too many documents to find | here |

### 2026-10-19 (the explorer's decisions of 2026-10-14 to 2026-10-18, recorded)

Made in UI sessions and kept until now only in the wireframe and session
notes. Reasons are the curator's where they were given; "not recorded" where
they were not.

| ID | Decision | Recorded in |
|---|---|---|
| D-101 | The stack (2026-10-14): Figma for design only; a React app with Cytoscape.js as the graph canvas and a map widget as a second canvas; a FastAPI read and command API in front of Neo4j. The UI shows only words the server works out, and every write goes through the proposal path. Code in a fresh `GraphRevised/explorer/`. Alternative turned down: adapting the legacy `viewer/` (20 §1 had it as ADAPT) | [26](26-UI-DATA-CONTRACT.md) §1; [20](20-EXPLORER-UI.md) §6 |
| D-102 | One input (2026-10-14, 2026-10-15): the bottom drawer takes search, jump, and commands in a single box, results popping up above it, with the breadcrumbs and the time slider; the front door uses the same box. No top bar and no separate search; persona and Layout sit on the stage row. Commands, not chat: the narrative is the Account stage mode. Alternative turned down: a chat panel (20, 26 §1 before 2026-10-19) | [26](26-UI-DATA-CONTRACT.md) §1; wireframe v7 |
| D-103 | The map is a centre-stage mode, taking the whole centre, with zoom (2026-10-14). The renderer is open: MapLibre with CAWM terrain and our own ancient labels (`explorer/experiments/map-terrain.html`), or Google photorealistic 3D tiles (needs a Map Tiles API key). Coordinates come from Pleiades or Wikidata through the API, never stored from a map provider (20 §4a) | [26](26-UI-DATA-CONTRACT.md) §1 |
| D-104 | Sidebars are compact and configurable (2026-10-14): each docked, floating over the stage, or hidden behind an edge tab, from a Layout menu, remembered per user. Defaults: Filters hidden, Details docked (260px in v7). Reason: the centre stage as large as possible | [26](26-UI-DATA-CONTRACT.md) §1; wireframe v7 |
| D-105 | Quiet chrome (2026-10-15): small type everywhere; the in-stage routes graph collapsed by default; wireframe annotations off by default. Reason: the stage stays large and the sidebars don't distract | wireframe v7 |
| D-106 | The hub (2026-10-18, wireframe v7): where you stand at the centre; an inner ring of ways of reading it (Account, Notes, Map, Family tree for a person, Video dashed); an outer ring of groups **by relationship**, not bare kind, with distinct-member counts ("Participants · 15"), plus dashed "Elsewhere in …" and "Not yet read". Clicking a group always makes it the new centre, with a breadcrumb step; an event's parts open as the phase spine (D-091). Display only, never stored (D-039). Replaces the screens strip and the stage tabs | [26](26-UI-DATA-CONTRACT.md) §1; wireframe v7 |
| D-107 | The Battle of Actium is the default view for testing (2026-10-15); "people first" is how agents discover, not the opening screen. Anything not in the export yet is drawn as mock | [29](29-EVENT-CENTRED-INQUIRY.md); wireframe v7 |
| D-108 | A family tree stage mode for people (2026-10-15), drawn top down: grandparents, parents, the person with siblings and spouses, children, a capped set of grandchildren | wireframe v7 (screen 7) |
| D-109 | Three personas (2026-10-14): a scholar studying linkages, a student who needs citations, a casual browser who doesn't. A persona changes the telling, never the facts (26 §5). Screen zero is the front door, "what is this?", with three answers: in the graph, not read yet (grow it), a new subject | [26](26-UI-DATA-CONTRACT.md) §5; wireframe v7 (screen 0) |
| D-110 | Wireframes are greyscale HTML built from the real export (`explorer/wireframes/build.py`, `template.html`), designed-but-not-built marked mock, imported into Figma as layers (`freeze_screens.py`). Video is a planned enhancement, shown dashed (2026-10-15) | `explorer/wireframes/` |
| D-111 | A relationship group over 20 members never opens as a ring (curator, 2026-10-19): it opens split by its next key, each sub-group a breadcrumb step. A person's events split by the events they are part of (a level everyone shares is passed through), then by whose telling they are; an event's members split by voice (the Work a depicted event belongs to); otherwise by kind. Phases come first, in the spine's order. Reason: 28 groups had more than 15 members (Antony's events 164, a phase's parts up to 93). Alternatives turned down: a capped ring with the rest listed in the sidebar; a sequence strip | [26](26-UI-DATA-CONTRACT.md) §1; wireframe v7 (screen 10) |
| D-112 | The hub's "Other" group split (curator, 2026-10-19): `described by` becomes the group "Works about it"; `happened before` is not a hub group, it orders members inside the spine and sequence views. Alternatives turned down: both as hub groups; keeping "Other" | [26](26-UI-DATA-CONTRACT.md) §1; wireframe v7 |
| D-113 | In a group split by source, a source is a short reference mark ("Weigall¹ · 31") and its full title a footnote on the stage ("Whose telling"), not "according to …" on every node (curator, 2026-10-19). A one-member group is not drawn; its member sits on the ring. A group's kinds line ("11 people, 4 groups") shows only when it mixes kinds. Refines D-111 | [26](26-UI-DATA-CONTRACT.md) §1; wireframe v7 (screen 10) |
| D-114 | Entity images come from the preserved Wikidata records (P18, else a locator map P242), each described by its Wikimedia Commons file page (author, licence, date, categories; the API responses cached as source payloads) and classed by rules a reader can check: of the time, a later imagining, the place today, an edition, a modern map, doubtful (never shown; listed for the curator), unclassed (curator, 2026-10-19). Only images of the time or of the place today stand for an entity on the canvas; the others appear on its card with their caption ("A later imagining: Laureys a Castro, 1672"). Wireframe first: images and their manifest are git-ignored data; image records in the graph come later through proposals (D-096). Reason: P18 is "an image", not a picture of the thing in its time (Actium's is a 1672 painting; Domitia's a generic "Roman girl"). Code: `adapters/commons_images.py` | [20](20-EXPLORER-UI.md) §3; D-096 |
| D-115 | The full name wherever you stand or navigate: the card, breadcrumbs, routes, the centre of the hub or a group; a short caption (`shortLabel`) only on crowded rings (curator, 2026-10-19). Reason: "Actium" alone reads as the place, and the graph also holds a 435 BC "Battle of Actium" | [26](26-UI-DATA-CONTRACT.md) §1; [02](02-GRAPH-MODEL.md) §1 |
| D-116 | The card is the centre stage when you stand on something; the graph takes the stage when its shape is the point (a group, a path, the phase spine, a family tree) or on "◎ Graph". The right column becomes a navigator, a small live hub, with what is selected elsewhere below it; a fact's voices open in place in the card (curator, 2026-10-19). Supersedes D-106's hub as the opening view (the hub stays, as the graph view). Reason: the card is what people read on arrival, and the hub only repeated its "Where to go from here". Alternatives turned down: no right column; per-persona defaults | [26](26-UI-DATA-CONTRACT.md) §1; wireframe v8 |
| D-117 | What floats closes when you are done with it: results with × Hide, Escape, or a click elsewhere; suggestions on a click elsewhere or Escape (curator, 2026-10-19) | [26](26-UI-DATA-CONTRACT.md) §1 |
| D-118 | Lenses carry an icon and a colour from the icon's material: military bronze red, social terracotta, political Tyrian purple, economic gold, religious flame amber, each with a lighter dark-mode value; colour only for the lens in use, never for status or attestation (curator, 2026-10-19). The icon sheet is from IconScout, its licence not yet confirmed: small icons drawn for the wireframe meanwhile, the sheet git-ignored. Alternatives turned down: red, purple, blue, and white (white cannot be a line colour); icons without colour | [26](26-UI-DATA-CONTRACT.md) §1; `explorer/images/lenses/lenses.json` |
| D-119 | No front door page (curator, 2026-10-19): the app opens on the default card (Battle of Actium, D-107) with the one input ready; its three answers (in the graph, grow it, a new subject) stay in the input's suggestions; ⌂ holds lives in the order they act and where you have been. Replaces D-109's screen zero. Reason: the page repeated the input, and its purpose was unclear. Alternatives turned down: first visit only; keep it | [26](26-UI-DATA-CONTRACT.md) §1 |
| D-120 | Notes on the stage are a book: two columns a page, page turns instead of a long scroll (curator, 2026-10-19) | [26](26-UI-DATA-CONTRACT.md) §1, §4a |
| D-121 | Type about 20% smaller across the explorer and Figma (body 10, chrome 9.5, card title 12, labels 9, canvas 7.5); long reading text (the account, notes, quotations) stays near 13 (curator, 2026-10-19). Alternative turned down: about 30% smaller, and shrinking reading text too | Figma text styles; wireframe v8 |
| D-122 | A theme choice, system, light, or dark, in the Layout menu and on the `t` key, remembered per user; the Figma Color variables carry both modes (curator, 2026-10-19) | [26](26-UI-DATA-CONTRACT.md) §1 |
| D-123 | Each kind has a small icon (person, event, place, group, office, work, concept, period, state, type), beside its name on a card and as the picture of a canvas node that has none (curator, 2026-10-19). Reason: shape alone did not say the kind | wireframe v8 |
| D-124 | "How it is read" high on the card: the subject's interpretive facts and one interpretation note per author, each saying whose reading it is, with its words and a link to the passage; the rest one click away (curator, 2026-10-19). Alternatives turned down: a separate readings stage; both | [26](26-UI-DATA-CONTRACT.md) §1 |
| D-125 | Canvas labels wrap to the width of two words a line rather than being cut short (curator, 2026-10-19) | wireframe v8 |
| D-126 | The breadcrumbs are a trail, not a log: going back to a place already on it cuts the trail to it; a long trail shows its start, "…", and its last four steps (curator, 2026-10-19) | [26](26-UI-DATA-CONTRACT.md) §1 |
| D-127 | As many sources as possible are links: a Work's name opens its text, a locator its passage, from the passage's own locator (the page and anchor at LacusCurtius, Gutenberg, the Wikipedia revision; a Scaife link for a Perseus CTS passage). The export carries `url` on each quotation. Wikidata (a system, kept quiet) and a curator's page numbers have none (curator, 2026-10-19). Code: `export/cytoscape.py` `passage_url` | [26](26-UI-DATA-CONTRACT.md) §3 |
| D-128 | A battle's participants open as an order of battle: its sides, their units, and who commanded them, from the "commanded" claims set in the battle, every line reading "commanded" (curator, 2026-10-19). The graph does not yet say which fleet a wing belongs to, nor most units' sides; the view spreads sides through shared commanders and the one "opposed" claim, places the rest by name (dashed), and lists what it placed so. Claims for the gaps (a wing `partOf` its fleet; a unit's side) are to come through proposals. Alternative turned down: the role written on each line of the ring | [26](26-UI-DATA-CONTRACT.md) §1 |
| D-129 | A battle's "part of" group is shown as "Moments of the battle · 174, in 11 phases": the sources' moments placed in the curator's phases (D-070, D-091) are sequence, not a relationship to label on a line (curator, 2026-10-19) | [26](26-UI-DATA-CONTRACT.md) §1 |

## 3. Open

Recorded where they are, not here, until decided: [31](31-ONE-COMMAND.md) §7
items 3-12; [32](32-RESEARCH-WORKSPACE.md) §3; [19](19-SESSION-HANDOFF.md) §5
"Open". When one is decided it gets an entry here.

## 4. A new entry

From D-001 on, a decision made in a session gets an entry with: the decision;
the date and who decided; the reason, in a sentence; the alternatives turned
down; the documents and code it changes. Long reasoning stays in its document;
the entry points to it.
