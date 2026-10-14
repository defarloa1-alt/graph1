# 26 — UI Data Contract

**Date:** 2026-10-13. **For:** the curator designing the explorer in Figma, and
whoever builds the read API. **Status:** shapes 2 and 3 are built (the export
emits them today); shapes 1, 4, 5, and 6 are specified here and not built.

The explorer never shows storage. Claims, Proposals, passages, and authority
records stay behind the read API; the UI receives a few plain shapes. This
document defines those shapes with real data from the graph as it stood on
2026-10-13 (Mark Antony and the Battle of Actium), messy cases included, so
designs meet what the graph actually returns.

## 1. The screen

```text
┌──────────────────────────────────────────────────────────────────────┐
│ top border: search · persona switch · lenses                          │
├───────────┬──────────────────────────────────────┬───────────────────┤
│ left      │                                      │ right             │
│ border:   │           CENTRE STAGE               │ border:           │
│ filters   │   people, places, events, works      │ details of what   │
│ (kind,    │   one line per fact                  │ is selected:      │
│ category, │   (shape 2), styled by status,       │ node card (1)     │
│ attest-   │   category, attestation              │ or fact card (2)  │
│ ation,    │                                      │ with its voices   │
│ source)   │                                      │ (3)               │
├───────────┴──────────────────────────────────────┼───────────────────┤
│ bottom border: time slider (shape 4)              │ CHAT: narrative   │
│ breadcrumbs of where the user has been            │ and questions (5) │
└───────────────────────────────────────────────────┴───────────────────┘
```

Where the chat sits is a design choice; the contract does not depend on it.
Principles (25 §5, §7): the user stands at the centre with **signposts** out
and **breadcrumbs** behind; provenance is sidebar text, never canvas nodes;
voices ("according to Plutarch") are content, source systems (Wikidata) are
quiet.

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
| `quotes[]` | `source`, `locator` ("Plutarch Antony 65.1"), verbatim `quotation`, `pending` (evidence not yet reviewed) |
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

## 5. Narrative — the chat and the card's story (specified)

Written by an agent from the graph only (25 §7). A persona changes the
telling, never the facts; the user can switch persona at any time.

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

## 8. Visual encoding summary

| Data | Values | Suggested encoding |
|---|---|---|
| Entity `kind` | Person, Group, Event, Place, Period, Work, Concept | Shape and colour |
| Entity `status` | proposed | Faded fill, dashed outline |
| Fact `status` | accepted, proposed | Solid, dashed |
| Fact `mode` | attributed | Hollow marker at the start ("according to") |
| Fact `category` | interpretive, imaginative | Distinct line style; imagined facts in their own colour lane |
| `attestation` | words | Badge; never a percentage |
| Authority codes (Wikidata, LCSH, FAST) | label plus code | **Never a code alone** (curator's rule): the authority's own words first, the code beside them, "Battle of Actium (31 B.C.) (FAST 796265)"; quiet, in the card's footer |

The smoke view ([export/cytoscape.py](export/cytoscape.py), output in
`exports/graph.html`) implements shapes 2 and 3 and this encoding, as a
reference for the Figma work.
