# Depicted Events and Passages of Note (E12)

**Status:** agreed with the curator, 2026-10-12 (decisions in §9). Implementation in progress.
**Builds on:** [22-CLAIM-QUALIFIERS.md](22-CLAIM-QUALIFIERS.md) (claim mode,
context, time), backlog E12 in [04](04-IMPLEMENTATION-PLAN.md), the use-case
response (annotations, roadmap Phase A).

## 1. What is already in place, and what is missing

Attributed claims exist: the reader drafts "according to Plutarch" claims,
each tied to its Work, and promotion to an asserted claim is a curator act.
Two kinds of content still fall through:

1. **Actions within an event.** Antony touring his ships in a row-boat,
   Caesar's right wing rowing backwards, Cleopatra's squadron sailing through
   the line, Antony's flight. These are the narrative's events, but the only
   event in the graph is the battle itself.
2. **Colour that is not an event.** Character, anecdote, omen, rhetoric,
   atmosphere: Caesar meeting the man with the donkey named Victory, Antony
   sitting alone at the prow after the flight, a speech's argument. Not
   claims about what happened, yet the reason people read these sources.

The guiding principle, agreed earlier: **narrative detail is the author's
depiction, not established fact.** Both kinds stay "according to" their
source.

## 2. Depicted events

### Model

A depicted event is an `Entity {kind: Event}` that belongs to one source's
narrative:

```text
(:Entity {kind: Event, id: chr:entity:depicted:<work>:<slug>,
          label: "Antony's flight (Plutarch)", status: proposed})
  ← claims, all attributed to the Work:
     <depicted event> partOf  Battle of Actium        (context: the battle)
     <person/force>   participatedIn <depicted event> (who did it)
     <depicted event> occurredAt <place>               (where, if stated)
     <depicted event> triggeredBy / resultedIn <depicted event>
     time qualifier: the source's marker ("at the sixth hour"), with a
                     relative offset from the battle when the source gives one
```

- **One depiction per source.** Plutarch's flight and Dio's flight are two
  entities. That they depict the same historical action is a separate,
  interpretive claim (`depictsSameAs`, asserted mode, curator only), which can
  be contested (E8). No merging is forced.
- **Order from time markers, not narration order.** Plutarch narrates out of
  sequence; ordering uses the relative offsets ("the fifth day", "the sixth
  hour") and `triggeredBy`/`resultedIn`, never the order of sections.
- **Promotion** of a depicted event to a historical event, or of its claims
  to asserted claims, stays a curator decision with a recorded basis
  (independent witnesses, scholarly consensus).

### Predicates (registry v5)

| Predicate | Subject → object | Notes |
|---|---|---|
| `participatedIn` (existing) | Person/Group → Event | who acted in the depicted event |
| `partOf` (existing) | Event → Event | the depicted event within the battle |
| `occurredAt` (existing) | Event → Place | where, if stated |
| `triggeredBy` | Event → Event | the source's causal or temporal link ("when he saw this") |
| `resultedIn` | Event → Event | the source's stated outcome |
| `depictsSameAs` | Event ↔ Event | asserted only; curator; links depictions across sources |

Goals and motives ("wishing to draw the enemy out") are the most interpretive
element. They are left to E11 (actor actions), and until then are kept as
passages of note (§3) rather than claims.

### Who creates depicted events

The reader may not create entities: identity is a curator decision. Depicted
events are a different case. They have no outside identity to get wrong;
they are the source's own narrative units, scoped to one Work.

**Proposed:** the reader may propose a depicted event, created with
`status: proposed`, together with the attributed claims about it. It is shown
in exploration at once, labelled as proposed ([25](25-LIVES-AND-PLAYGROUND.md)
decision 2; until 2026-10-13 it was hidden until accepted). Accepting the event follows the delegation
policy for attributed claims ([21](21-REVIEW-DELEGATION.md)); linking it to a
real-world identity or to another source's depiction remains the curator's.

## 3. Passages of note

### What they are

A passage of note records that a passage is worth reading for an entity, and
why, without asserting anything:

```text
(:Annotation {kind: passage-of-note, noteType: anecdote,
              note: "Caesar's meeting with a donkey-driver named Victory, taken as an omen",
              author: passage-reader, visibility: team, status: flagged})
  -[:ANNOTATES]->      (:SourceObservation)   with the verbatim quotation
  -[:CONCERNS]->       (:Entity)              one or more: Augustus, the battle
```

- **Not a claim.** No predicate, no truth value, nothing to promote. It never
  serves as a hop in path tracing (06 §13–15); it appears on entity and
  passage cards as an excerpt "according to Plutarch".
- **Note types:** characterization, anecdote, omen, motive or goal, speech
  or rhetoric, atmosphere, detail.
- **Checks:** the quotation must be verbatim in the passage (the existing
  validator check), and the concerned entities must be in scope.
- **Light review.** Notes appear as `flagged`; the curator can `endorse` or
  `dismiss` them. No acceptance gate, because nothing is asserted.

### Why an Annotation node

The use-case response already agreed on annotations as their own node type
(owner, visibility, freely deletable) for curator and user commentary.
Passages of note are the same thing written by an agent. One mechanism then
serves both, with visibility enforced by the read API. This adds an eighth
core label; the query that needs it is "show the colour around Antony at
Actium", which neither a claim nor a property can answer.

## 4. Reader changes

The reader's output gains two lists beside `claims`:

- `depicted_events`: label, quotation, participants, place, time marker,
  links to other depicted events in the passage;
- `notes`: note type, one-line note, quotation, concerned entities.

Guidance stays free of passage cues (rule 11 of the handoff). The prompt
asks for actions within the narrative event and for passages that add
colour, and states that both are the source's depiction.

## 5. Pilot

Read *Antony* and Dio 50–51 again with the new outputs. Done when:

1. the battle can be walked as each source tells it, step by step, ordered by
   time markers, every step quoted and labelled with its source;
2. the two sources' depictions sit side by side, with differences visible and
   no forced merge;
3. entity cards show passages of note for the main figures, each with its
   source and note type.

## 6. Interpretation

### A third kind of content

| Kind | Example | Whose voice | Where |
|---|---|---|---|
| Fact claim | Agrippa took part in the battle | Chrystallum's, by promotion | asserted claims (22) |
| Depiction | Cleopatra's squadron sails through the line | the ancient author's | attributed claims, depicted events (§2) |
| Interpretation | Actium decided whether Rome's centre of gravity lay East or West; a contest of conventional and unconventional war | a modern scholar's | **interpretive claims and notes (this section)** |

A modern historian's reading of what an event meant is neither a fact nor a
depiction. Example (curator's reading of Barry Strauss, *The War That Made
the Roman Empire*, 2022): Actium as "a struggle for the heart of the Roman
Empire", East or West; Europe as "the child of Imperial Rome that emerged
from this battle"; the battle as "two ways of war", conventional and
unconventional.

### Claim categories

Every predicate declares a **category** in the registry, `factual` or
`interpretive`, and each Assertion records it when created (existing claims
are factual; migration 002). Interpretive claims:

- are always attributed to a Work (a scholar's reading), never asserted by
  Chrystallum; promotion would mean adopting a scholar's interpretation and
  is not offered;
- may disagree with one another; recording that one reading contradicts or
  qualifies another is E8;
- are marked as interpretive hops in path tracing, so a path through them is
  never presented as fact (06 §15).

Interpretive predicates (registry v5):

| Predicate | Subject → object | Meaning |
|---|---|---|
| `exemplifies` | Event/Group/Person/Work → Concept | the scholar reads it as an instance of the concept |
| `ledTo` | Event → Event/Period/Group/Concept/Place | a long-range consequence in the scholar's reading, distinct from a narrative's `resultedIn` |
| `depictsSameAs` | Event ↔ Event | two sources' depictions are of one historical action (curator) |

### Kinds: Office and Concept

`Other` would otherwise hold offices, concepts, and leftovers, and queries
could not tell them apart. Two kinds are added (values of `Entity.kind`, not
labels):

| Kind | Holds | Identity |
|---|---|---|
| `Office` | positions and posts; targets of `heldPosition` and role qualifiers | DPRR (E17), Wikidata |
| `Concept` | analytical ideas, themes, frames; targets of `exemplifies` | Wikidata where one exists, else local, curator-approved |

Each Concept has a one-line definition, so near-synonyms are merged rather
than multiplied. Generic Concepts take the hub penalty in path tracing.
`Other` remains for what fits nothing yet.

### "Show me the interpretations of the battle"

The answer combines interpretive claims whose subject or object is the event
with passages of note of type `interpretation` that concern it, grouped by
Work and author and ordered by date of composition:

```text
Interpretations of the Battle of Actium
  Strauss, The War That Made the Roman Empire (2022)
    exemplifies -> conventional versus unconventional war   [claim, according to Strauss]
    ledTo -> the Western-centred Roman Empire              [claim, according to Strauss]
    "a struggle for the heart of the Roman Empire ..."     [passage of note, with locator]
```

It is the read operation `getInterpretations(entity)` in the Phase B API and
an "interpretation" filter in the explorer's right ribbon. Each Concept is a
doorway in turn: every event any scholar has read as an instance of it.

## 7. Capture: passages chosen while reading

Three channels, one path: a preserved passage, a note, and claims proposed
from it, never created directly.

1. **Agent capture** from open texts: the reader flags passages of note
   (§3).
2. **Manual capture** by the curator: work, edition, page or location, the
   quoted text, a note, and the entities it concerns (a command now; a form
   in the explorer later).
3. **Imports** of reading highlights: Kindle `My Clippings.txt` and
   Readwise/Reader CSV exports, which carry book, author, location, highlight,
   note, and time. A book is matched to an existing Work entity through a
   curated mapping; an unknown book is reported, never created.

Rules:

- **Curator transcription** is a SourceObservation kind: the quoted text as
  the curator or the import recorded it, with the edition and locator (a
  page, or a Kindle location, which is specific to that edition), who
  captured it, when, and from which import file.
- **The note is not the author's words.** The quotation is evidence of what
  the author wrote; the curator's note is an Annotation. They are stored
  separately, as editorial notes are kept apart from ancient text.
- **Rights.** Quotations from works in copyright are kept short and
  verbatim, and Annotations and transcriptions are **private by default**;
  making them visible to a team is the curator's explicit choice, enforced by
  the read API.

## 8. Implementation order

1. Registry v5: `Office` and `Concept` kinds, claim categories, the new
   predicates; migration 002 sets `category: factual` on existing claims.
2. Annotations (an eighth core label, unique `id`) with `ANNOTATES` and
   `CONCERNS`; curator transcriptions as a passage-like observation kind.
3. Capture command and the Kindle and Readwise importers.
4. Reader outputs for depicted events and passages of note; the pilot (§5).
5. `getInterpretations` with the Phase B read API.

### Progress (2026-10-12)

Steps 1–3 are done:

- Registry `predicates-v5` (categories, `Office` and `Concept`, the new
  predicates); migration 002 categorized the 52 existing claims.
- Annotation (migration 003 constraint) and transcription observations,
  with four operations (31 in all).
- [capture/](capture): `cli add` for one passage, `cli import` for Kindle
  `My Clippings.txt` and Readwise/Reader CSV, matched to Works through
  [curation/reading.json](curation/reading.json); imported files are kept in
  the git-ignored `private-sources/`. A live test carries a captured
  quotation through to an attributed, interpretive `exemplifies` claim on a
  Concept. 140 tests.

Before the first real capture, the curator adds each book read as a Work
(identity approval) and to `curation/reading.json`.

## 9. Curator decisions (2026-10-12)

All accepted as recommended:

1. The reader may propose depicted events, created `status: proposed` (§2).
2. Passages of note are Annotation nodes, shared with curator and user
   annotations (§3).
3. Depicted-event predicates: `triggeredBy`, `resultedIn`, `depictsSameAs`.
4. Goals and motives stay as passages of note until E11.
5. The interpretive layer: attributed-only interpretive claims, `exemplifies`
   and `ledTo`, Concept entities (§6).
6. Curator-entered passages from works in copyright, as short quotations with
   a locator (§7).

The curator added: passages will also come from personal reading (Kindle and
Readwise/Reader highlights), and kind `Other` should not carry concepts and
offices together (§6).
