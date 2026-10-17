---
status: governing
authority: the curator's workspace (plans as the curator sees them, notes, overlays, saved paths, status display)
depends_on: [02-GRAPH-MODEL.md, 31-ONE-COMMAND.md]
superseded_by: null
last_reviewed: 2026-10-17
---

# 32 — The Research Workspace: Notes, Overlays, Saved Paths, and Status

**Date:** 2026-10-17. **Status:** the curator's decisions are recorded in
[docs/Addendum  Curator Experience, Notes, Content, and Overlay Layers.md](docs/Addendum%20%20Curator%20Experience%2C%20Notes%2C%20Content%2C%20and%20Overlay%20Layers.md)
(§1 here); how they map onto the model (§2) is proposed; nothing is built.
**Changes:** [02](02-GRAPH-MODEL.md) (what an Annotation may concern),
[06](06-GRAPH-NAVIGATION.md) §13 (path tracing defaults),
[26](26-UI-DATA-CONTRACT.md) (status labels, filters), [29](29-EVENT-CENTRED-INQUIRY.md)
§10 item 6 (where the curator's notes live), [31](31-ONE-COMMAND.md) §7 items 1
and 2 (settled).

## 1. Decisions (curator, 2026-10-17)

1. **The user is the curator**, for now. The design serves one
   researcher-curator building, exploring, annotating, and governing the graph;
   a simplified experience for other users does not drive it.
2. **Line-item plans, low friction.** The plan is shown before costly or
   graph-changing work; every item has a stable id and may be approved,
   rejected, modified, or deferred, with **approve all** for routine plans;
   every version is kept. A run stops only for a material identity ambiguity, a
   major widening of scope, rights, a destructive reconciliation, or the budget.
   (Settles 31 §7 item 1: guided, with approve all.)
3. **The primary use is writing a book on the Roman Republic**: finding
   non-obvious relationships several hops away, with meaningful content, not
   nodes and edges alone. Four content layers: core knowledge (entities and
   approved claims), source voices (attributed depictions and readings),
   explanatory content (descriptions, accounts), and the research workspace
   (notes, questions, hypotheses, excerpts, saved paths).
4. **Notes are research objects**, creatable and editable from Obsidian and
   from the graph interface, attachable to an Entity, a claim, a passage, a
   Work, a Subject, a Proposal, a saved path, or another note. A note on a claim
   comments on it without becoming one.
5. **Obsidian is an editing client, not the authority.** Neo4j holds entities,
   claims, evidence, and stable ids; Markdown may hold extended personal prose.
   A note's id is stable across renames; an edited note never changes an
   approved claim; conflicts keep both versions.
6. **A core pack and overlays.** The governed graph (approved and attributed
   claims, authorities, sources, cleared quotations, approved accounts) is the
   core; private and shared overlays hold notes, highlights, transcriptions,
   hypotheses, saved paths, and candidate relationships, referencing core ids
   rather than copying them. What a user sees is composed at read time.
7. **Promotion from an overlay is a transformation**, not a visibility toggle:
   proposed, reviewed for evidence and rights, edited into a public form,
   decided by the curator, and linked back to its private origin without
   exposing private text. A model never declares copyrighted text cleared.
8. **Saved paths** are research objects: the nodes and claims of a multi-hop
   discovery, who found it, why it may matter, notes. Saving a path asserts
   nothing.
9. **Proposed claims stay visible in the same projection as approved ones**
   (25 decision 2, confirmed), with unmistakable status, because fit can only
   be judged in context. (Settles 31 §7 item 2.)
10. **Path tracing is approved-only by default**, proposed-inclusive when the
    researcher asks; every hop states its status, and a path with proposed or
    interpretive hops is a research lead, never a factual chain.
11. **Status is encoded redundantly** (line style and a card label, never colour
    alone): APPROVED; PROPOSED — NOT REVIEWED; CONTESTED; REJECTED and
    SUPERSEDED in history only.
12. **Match before storing**: a candidate claim is compared with approved and
    proposed claim families before another edge is made (31 §3.5).

## 2. Onto the model (proposed)

### 2.1 Notes are Annotations

No new label. The Annotation (02, the eighth core label) already is
commentary, never a claim, with an author, visibility, and status. It gains:

- `kind: note` beside `passage-of-note` and `entity-mention`, with the
  addendum's note types (observation, question, hypothesis, interpretation,
  excerpt, outline, argument) and its own statuses (draft, active, endorsed,
  archived);
- **wider targets**: `CONCERNS` may point at an Entity, an Assertion, a
  Subject, a Proposal, another Annotation, or a saved path, not only an Entity;
  `ANNOTATES` keeps the passage and its quotation;
- `title`, `body` (Markdown), `modifiedAt`, `origin` (obsidian, graph-ui,
  import, agent) and `filePath`, and a `quotationStatus` (private copy, public
  domain, licensed, permission, review required) set by the curator, never by
  a model.

29 §10 item 6 (option c) becomes concrete: the vault is the editor, the note's
id sits in its frontmatter, and the graph holds the note with its targets; a
sync tool reads designated folders, and the graph interface can open the note's
Obsidian URI.

### 2.1a The sync (decided by the curator, 2026-10-17; not built)

**The sync is a small program, outside Obsidian, that watches one folder of the
vault and makes the graph match the notes in it.** It writes notes into the
graph as transcriptions and Annotations; it never writes knowledge.

- **One way: vault to graph.** Notes are written in Obsidian; the graph holds
  the result. A note changed in the graph as well is not merged: both versions
  are kept and the curator is told (decision 5). Graph to vault comes later, as
  an export in the same format.
- **The folder:** `GraphRevised/obsidian_book_notes/` (the vault's root is the
  repository's). Only notes there marked `chrystallum: note` are
  read; nothing else in the vault, and never `.obsidian/`. The folder is
  git-ignored: the notes are private and quote books in copyright, and the
  repository is public.
- **A watcher:** it runs whenever a note in the folder is saved.

**The note's format.** Flat frontmatter (Obsidian's Properties panel edits
flat keys only), between `---` lines at the very top of the file; the
passage in a `> [!quote]` callout; the curator's own text after it.

```yaml
---
chrystallum: note         # the marker: notes without it are ignored
id:                       # left empty: the sync fills it
noteType: excerpt         # observation | question | hypothesis | interpretation | excerpt | outline | argument
status: draft             # draft | active (endorsed, archived: set in review)
visibility: private
book: "The War That Made the Roman Empire"   # the title as printed
author: "Barry Strauss"
isbn: ""                  # optional, from the copyright page: the surest identity
edition: "Simon & Schuster, 2022"
page: 3                   # or location: (a Kindle location)
work:                     # optional: the book's Entity id; the sync fills it when it finds the book
quotationStatus: private-copy   # private-copy | public-domain | licensed | permission | review-required
concerns:
  - chr:entity:battle-of-actium
---
```

**The book need not be in the graph** (curator, 2026-10-17): a note names its
book by `book` and `author` (and `isbn` where known), and `work` is optional.

What a run does with one note:

1. **Identity.** A new note is given an id, written back into its frontmatter.
   The id survives renames and moves.
2. **The book.** With `work` given, the id must exist, and `book` and
   `author` must agree with it (a disagreement is reported). Without it, the
   book is looked for in the graph, by ISBN, then by title and author:
   - one match: its id is written into `work` (the only other change the sync
     makes to a file);
   - more than one: nothing is stored for the note, and the curator is asked;
   - none: the book is **proposed** as a Work, and its author as a Person when
     no Person matches (both visible at once, labelled proposed); the book is
     looked up in a catalogue the registry lists, its record preserved, and
     *author authorOf book* drafted from that record, never from the note's
     typed words. Until such a catalogue is registered (its terms checked at the
     source, rule 17), the book is proposed without the authorship claim and
     listed as waiting for one. Wikidata identity stays the curator's.
   Nothing waits on the book: the transcription and the note are stored at once,
   linked to the Work found or proposed.
3. **Targets checked.** Every id in `concerns` must exist in the graph;
   otherwise the note is reported and nothing is stored or created.
4. **Written.** The quote block becomes a transcription (the book's words as
   printed, the locator, the edition, who captured it and when, private,
   `IN_WORK` the book); the curator's own text becomes an Annotation (theirs,
   never a claim), `ANNOTATES` the transcription with the words it is about and
   `CONCERNS` its targets. An excerpt (no text of the curator's) still gets
   its Annotation, with no note text, so that what it concerns is recorded.
5. **Remembered.** A hash of the note, so the next run knows what changed.

Edits and deletions:

- **The curator's text edited:** the Annotation is updated, the earlier text
  kept as history.
- **The quoted words edited:** a different passage, so a new transcription;
  the old one stays, since claims may cite it.
- **A note deleted:** its Annotation is withdrawn; the transcription and any
  claims drawn from it stay, with their own review history.
- **Never a claim:** an edited note never changes a claim (decision 5).
  Claims are drafted from a transcription by an agent and reviewed by the
  curator, a separate step.

### 2.2 Saved paths are Annotations too

`kind: path`, an ordered list of node and claim ids, `generatedBy` (curator or
agent), an explanation, visibility, and notes; `CONCERNS` to the nodes on the
path. A saved path may become a research question, a source-discovery task, or
an agent's assignment to test the connection (31 §3).

### 2.3 Overlays are visibility and ownership

The core pack is graph content (claims by status, Works, authorities, accepted
and endorsed Annotations); an overlay is the Annotations, transcriptions, and
saved paths of one owner at a visibility. The read API composes them; nothing
is copied. The run state gains an owner and a visibility
([orchestration/contracts.py](orchestration/contracts.py)), so a run's
candidates and notes belong to a workspace.

### 2.4 Promotion from an overlay

A command turns a private note or transcription into proposals: an attributed
or interpretive claim with a cleared quotation, or an endorsed public note,
each linked `PROMOTED_FROM` the private Annotation (the link stays private).

### 2.5 In the explorer (26)

- Card labels by status as in decision 11; a proposed claim's card shows who
  proposed it, the inquiry and run, when, its evidence and qualifiers, its
  validation, the critic's verdict, and possible duplicates or conflicts.
- Filters: approved only; approved and proposed (the default research view);
  proposed only; contested; attributed; interpretive; history (rejected,
  superseded); private overlay; shared overlay. A publication view defaults to
  approved only.
- Path tracing (06 §13): approved-only by default; including proposed claims is
  a switch, and every hop's status is in the explanation.

### 2.6 The sequence (2026-10-17, handoff 1f2(g))

From the sequence-diagram review, adapted: the sync runs vault to graph,
one way (§2.1a), and promotion makes new
proposals rather than changing a note's visibility (decision 7). Nothing here
is built.

```mermaid
sequenceDiagram
    autonumber
    actor Curator
    participant Vault as Obsidian vault
    participant Sync as Sync tool
    participant Graph as Graph
    participant FD as Front door
    participant Store as proposals/

    Curator->>Vault: write a note (its id and targets in the frontmatter)
    Vault->>Sync: designated folders
    Sync->>Graph: the targets exist? (Entity, claim, passage, Work, Subject, path, note)
    Graph-->>Sync: yes, or the missing ids
    Sync->>Graph: Annotation kind note, private, CONCERNS its targets
    alt a note or a hypothesis
        Graph-->>Curator: shown over the core graph, labelled as the curator's
    else a question worth researching
        Curator->>FD: a bounded inquiry from the note
        FD-->>Curator: a line-item plan (31 §3.2)
    end
    opt promote from the overlay
        Curator->>Store: an attributed or interpretive claim, or a public note
        Store->>Store: validated, quotation rights set by the curator
        Store->>Graph: proposed, PROMOTED_FROM the private note (the link stays private)
    end
    Note over Vault,Graph: An edited note never changes an approved claim,<br/>a conflict keeps both versions (decision 5).
```

## 3. Open

1. **Visibility words.** Annotations use private, team, public; the addendum
   uses private, shared, public. Recommended: shared, renaming team (a
   migration of 71 Annotations).
2. **Saved paths as Annotations** (§2.2) or a label of their own. Recommended:
   Annotations, until a query needs more.
3. ~~**Which way sync runs first**~~ **Decided 2026-10-17 (curator):** vault
   to graph, one way, a watcher on `GraphRevised/obsidian_book_notes/` (§2.1a).
