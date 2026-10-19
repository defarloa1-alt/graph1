---
status: governing
authority: what the explorer receives (the shapes behind the read API)
depends_on: [02-GRAPH-MODEL.md, 29-EVENT-CENTRED-INQUIRY.md, 32-RESEARCH-WORKSPACE.md]
implemented_by: [export/cytoscape.py]
superseded_by: null
last_reviewed: 2026-10-19
---

# 26 — UI Data Contract

**Date:** 2026-10-13. **For:** the curator designing the explorer in Figma, and
whoever builds the read API. **Status:** shapes 2 and 3 are built (the export
emits them today); shapes 1, 4, 4a, 5, and 6 are specified here and not built.

The explorer never shows storage. Claims, Proposals, passages, and authority
records stay behind the read API; the UI receives a few plain shapes. This
document defines those shapes with real data from the graph as it stood on
2026-10-13 (Mark Antony and the Battle of Actium), messy cases included, so
designs meet what the graph actually returns.

## 1. The screen

**Revised 2026-10-19** to match wireframe v8 and the UI decisions D-101 to
D-129 ([33](33-DECISIONS.md)). The earlier sketch, with a top bar, a top
search box, and a chat panel, is replaced; so is v7's hub as the opening
view (D-116).

```text
┌──────────────────────────────────────────────────────────────────────┐
│ stage row: routes ▾ · lens · where you stand · ◎ Graph · persona · Layout │
├───────────┬──────────────────────────────────────┬───────────────────┤
│ filters   │            CENTRE STAGE              │ navigator: a      │
│ (hidden   │                                      │ small live hub of │
│ behind an │   the card (shape 4) when you stand  │ where you stand   │
│ edge tab  │   on something: image, what it is,   │ and its groups    │
│ by        │   where to go from here, when (a     │ ─────────────────  │
│ default)  │   date opens its fact in place),     │ what you select   │
│           │   sources, notes                     │ elsewhere: a fact │
│           │                                      │ (2, 3), a passage,│
│           │   the graph when the shape is the    │ another node      │
│           │   point: a group, a path, the phase  │                   │
│           │   spine, a family tree; or the       │                   │
│           │   account, notes (as pages), the map │                   │
├───────────┴──────────────────────────────────────┴───────────────────┤
│ command drawer: breadcrumbs · ⌂ lives and recent · the one input ·    │
│ results (× Hide, Esc, or a click elsewhere) · time slider · undated   │
└──────────────────────────────────────────────────────────────────────┘
```

- **The card on the stage** (D-116): standing on something opens its card
  on the stage, read like a page; every name is a door, "Where to go from
  here" opens a group on the graph, and a date opens its fact and voices in
  place. "◎ Graph" shows the hub around where you stand; "▤ Card" returns.
  The right column is the **navigator**, a small live hub, so the network
  stays in view beside the card; below it, whatever is selected elsewhere.
- **How it is read** (D-124): high on the card, the subject's readings:
  its interpretive facts, each with whose reading it is, a quotation, and a
  link to the passage; then one interpretation note per author, marked as
  the reader's summary; "All N readings" opens the notes at interpretation.
- **Order of battle** (D-128): a battle's participants open as its two sides,
  each with its fleets, wings, land armies, and squadrons, and who
  commanded them, from the "commanded" claims set in the battle; what the
  claims do not say (a wing's fleet, some sides) is placed by name, dashed,
  and listed in a footnote.
- **Names** (D-115): the full name wherever you stand or navigate (card,
  breadcrumbs, routes, the centre of the hub or a group); short captions only
  on crowded rings.
- **The graph** (D-106, now one view among others): clicking a relationship
  group makes it the new centre, its members around it, with a breadcrumb
  step. For an event, "Part of, and its parts" opens as the phase spine, the
  curator's phase order (D-091), each phase with the number of events placed
  in it. Groups are computed for display and never stored (D-039). A group
  over 20 members opens split by its next key, never as a big ring (D-111):
  a person's events by the events they are part of, then by source; an
  event's members by source, each a short reference ("Weigall¹ · 31") with
  its title in a footnote on the stage (D-113); otherwise by kind.
  `described by` is the group "Works about it"; `happened before` orders
  members and is not a group (D-112).
- **The command drawer** (D-102, D-117): one input for search, jump, and
  commands (`jump`, `why A and B`, `elsewhere 31 BC`, `note`, `cite`, `as`,
  the stage modes). Suggestions pop up above it and close on a click
  elsewhere; results close with × Hide, Escape, or a click elsewhere. There
  is no front door page (D-119): the app opens on the default card; ⌂ holds
  lives in the order they act and where you have been. It is commands, not
  chat; the narrative is the Account stage mode (shape 5).
- **Notes** (D-120): two columns a page, turned with ‹ ›, the arrow keys, or
  a swipe; the type chips jump to the page where a type starts.
- **Lenses** (D-118): military, social, political, economic, religious, each
  with an icon and a colour from its material, shown only for the lens in
  use.
- **The sidebars** (D-104): each is docked, floating over the stage, or
  hidden behind an edge tab, set from the Layout menu and remembered per
  user, with the theme: system, light, or dark (D-122).
- **The map** (D-103) and the **family tree** (D-108) are stage modes that
  take the whole centre.

Principles (25 §5, §7): the user stands at the centre with **signposts** out
and **breadcrumbs** behind; provenance is sidebar text, never canvas nodes;
voices ("according to Plutarch") are content, source systems (Wikidata) are
quiet. Small type and quiet chrome, so the stage stays as large as possible;
long reading text stays comfortable (D-105, D-121).

## 2. Fact edge — a line on the canvas (built)

One line per fact: every claim with the same subject, predicate, and object,
from every source, drawn once. Imagined versions of a fact are a separate
line (`category: imaginative`). The graph currently has 37 facts held by 96
claims; the canvas draws 34 lines (the other 3 have no object and sit on
their node).

| Field | Meaning | Design use |
|---|---|---|
| `sentence` | Plain sentence | Card title, hover text |
| `label` | Short predicate ("participated in") | Text on the line |
| `category` | factual, interpretive, imaginative | Line style; filter |
| `status` | accepted, proposed (rejected and superseded only in audit) | Solid versus dashed |
| `mode` | asserted (we state it) or attributed (only sources say it) | Marker at the line's start |
| `attestation` | Words, never a number | Badge on the card; filter |
| `times` | Each source's own time words | "When" row; may disagree |
| `voices` | Shape 3, one per source | The card's body |

Attestation values: *well attested (N authors)*, *attested (1 author)*,
*disputed (N authors)*, *one author's reading*, *a reading shared by N
authors*, *imagined*, *no evidence yet*. Today the graph has 16 well
attested, 16 attested, and 2 readings.

Real example (trimmed):

```json
{
  "id": "chr:assertion:mark-antony:participated-in:battle-of-actium#factual",
  "source": "chr:entity:mark-antony",
  "target": "chr:entity:battle-of-actium",
  "label": "participated in",
  "sentence": "Mark Antony participated in Battle of Actium",
  "category": "factual",
  "status": "accepted",
  "mode": "asserted",
  "attestation": "well attested (4 authors)",
  "times": [],
  "voices": ["…five voices, shape 3…"]
}
```

An interpretation looks the same but reads differently:

```json
{
  "sentence": "Battle of Actium exemplifies decisive battle",
  "category": "interpretive",
  "status": "proposed",
  "mode": "attributed",
  "attestation": "one author's reading",
  "voices": [{ "accordingTo": "Hale, Famous Sea Fights",
               "quotes": [{ "locator": "Hale 2.1",
                            "quotation": "Actium was one of the decisive battles of the world" }] }]
}
```

## 3. Voice — who says it, on what words (built)

Each claim behind a fact. The fact card lists voices; the review history is
collapsed by default.

| Field | Meaning |
|---|---|
| `accordingTo` | The Work ("Plutarch, Life of Antony"), or `null` for our own statement |
| `status` | This source's version: accepted or proposed |
| `time`, `role`, `context` | This source's terms ("2 September 31 BCE", "as legate", "during Battle of Actium") |
| `quotes[]` | `source`, `locator` ("Plutarch Antony 65.1"), `url` (where a reader can open the passage: the page and anchor at LacusCurtius, Gutenberg, or the Wikipedia revision; a Scaife reader link for Perseus; none for a curator's page number; built 2026-10-19), verbatim `quotation`, `pending` (evidence not yet reviewed) |
| `review[]` | `operation`, `status`, `decidedBy`, `decidedAt`: the audit trail |

Real example:

```json
{
  "accordingTo": "Cassius Dio, Roman History",
  "status": "proposed",
  "time": null,
  "quotes": [{
    "source": "Cassius Dio, Roman History",
    "locator": "Cassius Dio 50.31.6",
    "quotation": "Antony, accordingly, fearing this flanking and encircling movement, advanced to meet it as best he could, and thus reluctantly joined battle with Caesar.",
    "pending": true
  }],
  "review": [{ "operation": "create", "status": "submitted", "decidedBy": null }]
}
```

## 4. Node card — what the user stands on (partly built)

Built today: `id`, `label`, `kind`, `status`, `description`, the facts that
have no object, and the notes. Not built: the narrative, signposts, and
the authority line.

| Field | Meaning | State |
|---|---|---|
| `label`, `kind`, `description` | "Mark Antony", Person, "Roman politician and general (83 BC – 30 BC)" | built |
| `status` | provisional, resolved, proposed (dashed outline when proposed) | built |
| `facts[]` | Facts with no object (when something occurred), in shape 2 | built |
| `notes[]` | Passages of note: type (motive, characterization, anecdote…), one line, source | built, ungrouped |
| `narrative` | Shape 5, for the chosen persona | not built |
| `signposts[]` | Doors out: `{label, count, state}`, state `explored` or `not yet read` | not built |
| `authority[]` | Quiet footer: one record per system, the identity first, the best-supported identifier shown and the rest counted ("Cleopatra in VIAF (VIAF 67762941) and 7 more"); never a code alone | built (2026-10-14) |

Signposts for Antony as the graph stands, for mock-ups: *Battles (1)*,
*Commands (4)*, *Cleopatra*, *Octavian*, *Elsewhere in 31 BC (empty)*,
*Not yet read: his life before 32 BC*.

## 4a. Notes stage — the stage switched to a node's notes (specified)

Added 2026-10-15 (curator). The user can switch the centre stage from **facts**
(the default: nodes and lines) to **notes** for the node they stand on: every
passage of note that concerns it, as cards on the stage rather than a list on
its node card. The node stays the centre; switching back returns to the facts.

| Field | Meaning |
|---|---|
| `focus` | The node the notes concern (`id`, `label`, `kind`) |
| `groups[]` | Notes grouped by `type` (interpretation, motive, detail, characterization, anecdote, atmosphere, speech, omen), each group ordered by Work, then passage |
| `note.text` | The reader's or curator's one line, shown as theirs, never as the author's words |
| `note.quotation`, `note.locator`, `note.accordingTo` | The author's verbatim words, where, and whose Work ("Weigall, The Life and Times of Cleopatra") |
| `note.alsoConcerns[]` | The other entities the note concerns: doors to their notes stages |
| `note.factsFromPassage[]` | Facts (shape 2) drawn from the same passage, so the colour sits beside the facts |
| `note.status` | flagged or endorsed (dismissed only in audit) |
| `note.mentions[]` | **Open** (not in the graph yet): the words in the passage that refer to the focus ("her ships"), to highlight why the note is on this stage |

Real example: *Cleopatra's squadron at Actium* has five notes today (Hale 2.12
atmosphere, "the state galley of Cleopatra, a floating palace"; Hale 2.24,
Weigall 17.5 and 17.19 interpretation; Weigall 17.14 detail) beside three facts
(participated in Actium, according to Plutarch and to Hale; commanded by
Cleopatra, according to Weigall). The query behind it is in
[views/actium-annotations.cypher](views/actium-annotations.cypher).

## 5. Narrative — the Account stage and the card's story (specified)

**Revised 2026-10-16.** For an event, the narrative starts from Chrystallum's
account ([29](29-EVENT-CENTRED-INQUIRY.md) §4, §4a): one stored,
researcher-grade text, every statement citing a preserved passage, which may
draw on passages the graph has not turned into claims (this replaces "from
the graph only", 25 §7). Persona retellings come later and are generated from
the account. A persona changes the telling, never the facts or the sources;
the user can switch persona at any time. The account's linked names give
`refs` to entities and events as well as to facts.

```json
{
  "persona": "explorer",
  "paragraphs": [
    { "text": "In the middle of the battle, Cleopatra's ships raised their sails and slipped away.",
      "refs": ["chr:assertion:cleopatra:participated-in:battle-of-actium#factual"] }
  ],
  "voicesInDispute": ["Plutarch", "Cassius Dio", "Hale", "Weigall"],
  "endsAt": "Not yet read: Antony before 32 BC"
}
```

Each paragraph's `refs` point to facts, so a tap opens the fact card and its
voices: the footnotes stay one tap away and never clutter the text.

**For an event's account (2026-10-17, [29](29-EVENT-CENTRED-INQUIRY.md)
§4b),** the paragraphs are the account's statements, and each carries its
`kind` (source, synthesis, signpost), so our own reading is shown as ours and
a signpost as a door. A source statement's `refs` are its claims and its
passages (locator and words, for the footnote); a synthesis's are the
statements it rests on; the linked names give entity `refs`. Sections carry
their phases, so the stage can follow the account through the battle.

## 6. Timeline item — the slider (specified)

| Field | Meaning |
|---|---|
| `label` | "Battle of Actium" |
| `when` | Display text: "2 September 31 BCE" |
| `earliestYear`, `latestYear` | Sort and placement; BCE negative |
| `fact` | The fact id, to open its card |
| `attestation` | As on the fact |

Only two claims in the graph are dated to the year today: Actium (2 September
31 BCE, from Hale) and Antony's authority over his land army (32–31 BCE).
Most claims are undated; the slider needs an "undated" tray.

## 7. Messy cases to design for

These are real, not hypothetical:

1. **A crowded card.** Antony has 75 passages of note. Group them by type
   (motive 22 across the graph, interpretation 39, detail 29…) and show a few.
2. **Sources that disagree on wording.** Actium's date has three voices: Hale
   gives "2 September 31 BCE", Dio gives "the second of September" twice (a
   near-duplicate the graph should merge). Show the source's words, not one
   cleaned-up date.
3. **Long quotations.** Dio's run to 150 characters; Weigall's longer.
   Truncate with expand.
4. **The wrong name for the time.** Octavian is stored as "Augustus" (his
   Wikidata label), so cards read "Augustus commanded … at Actium" in 31 BC,
   four years before he took that name. Names that change over time are an
   open design item for L3.
5. **A fact with only our own statement and no evidence** after its evidence
   was rejected: attestation then comes from the other voices; if there are
   none, "no evidence yet".
6. **Proposed entities.** 13 entities are proposed (two Periods, eleven Works);
   draw them, marked, never hide them.
7. **Review noise.** Some voices carry six "add evidence" records, including
   clean-up rejections. Keep the review history collapsed.
8. **A note whose quotation does not name the focus.** Weigall 17.14 is on the
   squadron's notes stage with the words "all the fleet was ordered to ship its
   big sails"; the squadron is named elsewhere in the paragraph, or not at all.
   Only about a third of the links from notes to entities are named in the
   note's quotation (98 of 288). Until mentions exist, show the full passage
   one tap away.
9. **A passage that names the focus but whose note is not tagged to it.** Hale
   2.25 and 2.26 say "squadron", yet their notes concern other entities, so
   they do not appear on the squadron's stage.

## 8. Visual encoding summary

| Data | Values | Suggested encoding |
|---|---|---|
| Entity `kind` | Person, Group, Event, Place, Period, Work, Concept, Office, Polity, Type | Shape and colour |
| Entity `status` | proposed | Faded fill, dashed outline |
| Fact `status` | accepted, proposed | Solid, dashed |
| Fact `mode` | attributed | Hollow marker at the start ("according to") |
| Fact `category` | interpretive, imaginative | Distinct line style; imagined facts in their own colour lane |
| `attestation` | words | Badge; never a percentage |
| Stage mode | facts, notes | A switch on the stage; notes grouped by type, each card quoting its source |
| Authority codes (Wikidata, LCSH, FAST) | label plus code | **Never a code alone** (curator's rule): the authority's own words first, the code beside them, "Battle of Actium (31 B.C.) (FAST 796265)"; quiet, in the card's footer |

The smoke view ([export/cytoscape.py](export/cytoscape.py), output in
`exports/graph.html`) implements shapes 2 and 3 and this encoding, as a
reference for the Figma work.

**Tokens and components in Figma (2026-10-19).** The wireframe's greyscale is
now the "Chrystallum Explorer" Figma file's foundations: a `Color` collection
(Light and Dark, the nine wireframe colours, each with its CSS name as code
syntax, `var(--ink)`), a `Size` collection (spacing and radii), text styles in
Atkinson Hyperlegible and IBM Plex Mono, and a float shadow. The page
"Components (2026-10-19)" holds Button, Segment, Chip, Pill, Attestation badge,
Signpost, Command input, and the canvas set: Canvas node (kind × status), Focus
node, Fact line (category × status × mode), Hub group, Reading node, drawn as
the wireframe's Cytoscape stylesheet draws them. Colour by kind is not decided.
