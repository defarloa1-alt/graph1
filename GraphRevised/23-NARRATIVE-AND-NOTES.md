# Depicted Events and Passages of Note (E12)

**Status:** draft for curator review, 2026-10-12. Nothing here is implemented.
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
`status: proposed`, together with the attributed claims about it. It is hidden
from exploration until accepted. Accepting the event follows the delegation
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

## 6. Decisions for the curator

1. **Depicted events created by the reader** with `status: proposed` (§2),
   instead of a curator identity act for each one? Recommended: yes.
2. **Passages of note as Annotation nodes**, shared with curator and user
   annotations (§3), instead of a relationship-only design? Recommended: yes.
3. **Predicates** for depicted events (§2 table): `triggeredBy`,
   `resultedIn`, `depictsSameAs`. Recommended: these three, no more until the
   pilot shows a need.
4. **Goals and motives** kept as passages of note until E11. Recommended: yes.
