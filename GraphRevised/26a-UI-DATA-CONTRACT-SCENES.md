---
status: draft
authority: what the explorer receives for movement, flybys, and pictures found or made (shapes 7 to 9)
depends_on: [26-UI-DATA-CONTRACT.md, 02-GRAPH-MODEL.md, 29-EVENT-CENTRED-INQUIRY.md, 31-ONE-COMMAND.md, 32-RESEARCH-WORKSPACE.md]
implemented_by: [adapters/commons_images.py (pictures found), explorer/images/generated/*.json (pictures made), explorer/wireframes/build.py (gallery, backdrops)]
superseded_by: null
last_reviewed: 2026-11-24
---

# 26a — Scenes, pictures and generated media (addendum to 26)

**Date:** 2026-11-24 (D-176). **For:** the curator designing the stage modes,
and whoever builds the read API, the orchestrator's generation steps, and the
renderers. **Status:** pictures found (Commons and Wikipedia) and one generated
backdrop are built and shown in the wireframe; movement, flyby, the 3D model and
video are specified here and not built. Shapes 7, 8 and 9 are new; the node card
(shape 4) gains four fields (§6).

This addendum adds the stage modes that draw *where and how things moved* and
*what they looked like*, and the way they are requested. The rule that governs
all of it: **the agent writes a plan, never a fact.** What is drawn comes from
the graph, or from a Proposal the curator can see and reject, or is a
**Generalized Abstraction** (D-172), marked as one.

Revised on 2026-11-24 from a first draft (written in a chat; this file replaces it): movement
kinds now use the curator's term, Generalized Abstraction (D-172); paid
requests become steps of the front door's plan (D-174) run by the guided
orchestrator (D-175), not a separate job system; the media record grows from
the generated-picture record already in use; Movement is the Animation view
drawn on the map, not a new mode; and the draft's facts were checked against the
graph.

## 1. Principles

1. **Draw from data first.** Movement and flybys are rendered from entities,
   Place `coordinates`, phases (D-091) and Proposals. Generation (images, 3D,
   video) is used only where the graph has nothing to draw, such as the look of
   a ship or the sea at Actium.
2. **An uncited position is not a fact (D-172).** A position or a path that no
   passage states is a **Generalized Abstraction**: a drawing to orient the
   reader. It is labelled so, drawn apart from sourced moves, and never stored
   as a claim.
3. **Pictures say what they are.** Every picture carries its class (§4): of the
   time, a later imagining, a reconstruction, the place today, a map, or
   generated. A generated picture is `category: imaginative` with the
   attestation word *imagined*; it never raises a fact's attestation and is
   never cited as a voice.
4. **The agent proposes; the curator approves.** A scene or a picture the agent
   makes enters as `status: proposed` and is drawn dashed until the curator
   accepts it. A request that costs money is a step of a plan, with its
   estimate, and waits for approval before anything is spent (§5).
5. **Order, not clock.** Few facts carry a year (64 of 2,119 lines in the export
   of 2026-11-24), and most of what happens inside a battle has only the
   source's time words. Movement is sequenced by the curator's phase order
   (D-091) and by `happened before` (26 §1), not by a time slider. The slider
   keeps its "undated" tray.
6. **Source words stay the source's.** A leg shows the source's own time words
   and quotation, never one cleaned-up date.
7. **The name of the time.** A caption, a label on a scene, and a generation
   prompt use the name a person bore in the scene's year, not the current label
   (Octavian at Actium, not Augustus; see the direction "names over time",
   not yet built).

## 2. Stage modes and requests

The stage modes of 26 §1 already include Map and Animation (the phase spine).
This addendum extends them; it adds one mode, Flyby.

| Mode | Where | What it shows | Data | State |
|---|---|---|---|---|
| **Movement** | The Animation view drawn on the Map (D-103), taking the whole centre | Units moving between places, phase by phase, with the order of battle (D-128) as the legend | Shape 7, `type: movement` | specified |
| **Flyby** | A stage mode that takes the whole centre | A scripted camera path over terrain, with the same legs and labels | Shape 7, `type: flyby` | specified |
| **Poster** | The cover of a battle's Participants group (D-173) | The order of battle over a generated backdrop, the two leaders' portraits from their time | Shape 8 records with `use: backdrop` and `use: portrait` | built (wireframe) |
| **Pictures** | On the card (shape 4), after the head | The pictures held for the entity, each with its class, caption and credit | Shape 8, `origin: found` | built (wireframe) |
| **Model** | A viewer inside the card, above "Where to go from here" | A rotatable 3D model or a still, always captioned *imagined* | Shape 8, `kind: model3d` | specified |

Commands in the one input (D-102). Like the others, they are commands, not
chat. A command that would call a paid service does not run: it adds a step to
the plan of the event's inquiry (§5), which the curator approves.

| Command | Does |
|---|---|
| `move Actium` | Open Movement with the accepted legs; propose a plan step to find missing ones |
| `fly Actium` | Propose a plan step that builds a Flyby spec; open it when ready |
| `picture Actium` | Propose a plan step for one still image |
| `model Cleopatra's squadron` | Propose a plan step for a still, then (after the still is accepted) a 3D model |
| `video Actium` | Propose a plan step for a stylised clip; not in the first release (§11) |

## 3. Shape 7 — Scene spec: a plan the renderers draw (specified)

One spec per request. Its `id` is a hash of its content, so the same request
returns the same stored result.

| Field | Meaning | Design use |
|---|---|---|
| `id` | Hash of the spec | Cache key; never shown |
| `type` | `movement` or `flyby` | Which stage mode opens |
| `subject` | The entity the scene is about (`id`, `label`, `kind`) | Stage title |
| `sequenceBy` | `phase` (default), `order` (by `happened before`), or `time` (only where every leg has dated terms) | How the scrubber steps |
| `status` | `proposed` or `accepted`; the spec as a whole | Dashed or solid frame |
| `proposedBy` | `agent` or the curator's name; with `proposedAt` | Review note |
| `legs[]` | The moves (below) | The animation |
| `camera` | For `flyby`: `{path: [{at, target, altitude, heading, pitch}], duration, followLegs}` | The camera script |
| `layers[]` | `terrain`, `places`, `unitPaths`, `labels`, `orderOfBattle` | Layer switches |
| `terrain` | `{source, note}`: `modern`, or `ancient` when an ancient coastline is held (§11) | A caption: "modern terrain; the ancient coast differed" |
| `footnote` | What the spec leaves out (a wing with no place, a unit with no side) | Footnote on the stage, as for the order of battle |

**Leg** (one move of one unit):

| Field | Meaning |
|---|---|
| `unit` | The entity that moves (a fleet, wing, squadron, or person) |
| `side` | From the order of battle (D-128); `null` if the claims do not place it |
| `from`, `to` | Place entities; their `coordinates` come from the Place card. A Place with none goes in the "Not on the map" tray and its leg is drawn as a label, not a line |
| `via[]` | Optional waypoints: Place entities, or `{lat, lon}` for a point we added (which makes the leg an abstraction) |
| `phase` | The phase of the event the leg belongs to (D-091); `order` is its position within the phase |
| `timeWords` | The source's own time words ("in the middle of the battle"); may be empty |
| `basis` | `sourced`, or a Generalized Abstraction: `inferred` or `illustrative` (below) |
| `voices[]` | Shape 3, trimmed: `accordingTo`, `locator`, `url`, `quotation`. Empty only for `illustrative` |
| `alternatives[]` | Ids of legs that disagree with this one (same unit, another place or order); each carries its own voices |
| `status` | `proposed`, `accepted`, `rejected` (audit only) |

`basis` values:

- **sourced:** a passage states this move between named places. Drawn solid.
  Once accepted it is also a fact (shape 2) with the voices as its claims, so
  it appears on the unit's card. The predicate is to be named by the curator
  (§11, question 1).
- **inferred** (a Generalized Abstraction): both ends are sourced, but the path
  between them, or the order, is ours. Drawn dashed and labelled "our line".
  It lives in the scene only and is never stored as a claim.
- **illustrative** (a Generalized Abstraction): no passage; added so the
  picture reads (an idle fleet at its anchorage). Drawn faded and labelled.
  Hidden when the persona is scholar or student and "imagined" is off (§7).

Example (trimmed; ids in angle brackets are placeholders not yet read from the
graph):

```json
{
  "type": "movement",
  "subject": { "id": "chr:entity:battle-of-actium", "label": "Battle of Actium", "kind": "Event" },
  "sequenceBy": "phase",
  "status": "proposed",
  "proposedBy": "agent",
  "legs": [{
    "unit": "chr:entity:cleopatra-squadron-at-actium",
    "side": null,
    "from": "chr:entity:<anchorage>",
    "to": "chr:entity:<open-sea>",
    "phase": "chr:entity:<phase-of-the-battle>",
    "order": 3,
    "timeWords": "in the middle of the battle",
    "basis": "inferred",
    "voices": [{
      "accordingTo": "Cassius Dio, Roman History",
      "locator": "Cassius Dio 50.31.6",
      "quotation": "Antony, accordingly, fearing this flanking and encircling movement, advanced to meet it as best he could, and thus reluctantly joined battle with Caesar."
    }],
    "alternatives": [],
    "status": "proposed"
  }],
  "terrain": { "source": "modern", "note": "the ancient coastline differed" },
  "footnote": "Not placed by the claims: Cleopatra's squadron before the battle."
}
```

The Dio quotation is a stored passage; it is shown because it sits in the same
phase, not because it states this move, which is why the leg is `inferred`. A
leg is `sourced` only if its passage states the move.

## 4. Shape 8 — Picture record: found or made (partly built)

One record per picture, whether found (a Commons file, from an entity's
Wikidata record or a Wikipedia article we hold) or made (generated). The card's
Pictures and Model viewer, the poster and any canvas portrait read this shape.

It grows from the two records already written: the gallery entries of
`adapters/commons_images.py` (`explorer/images/gallery.json`) and the generated
records in `explorer/images/generated/*.json`. Field names in brackets are the
ones those files use today.

| Field | Meaning | Design use | State |
|---|---|---|---|
| `id`, `kind` | `image`, `model3d`, or `video` | Which viewer | image built |
| `origin` | `found` or `made` | Footer wording | built (by file) |
| `file`, `thumbnail`, `page` | The file held (a GLB for `model3d`); its Commons page for a found one (`commonsFile`, `page`) | The viewer; "on Commons" link | built |
| `class` | Found: `of-the-time`, `later-imagining`, `reconstruction`, `place-today`, `map`, `doubtful`; made: `generated` (`illustration-generated`) | The caption's first words ("From their time", "A later imagining", "A modern reconstruction") | built |
| `depicts[]` | Entities shown: doors to their cards (found: from the caption's links, else the article's entity; made: `for`) | Caption links | built |
| `use` | `card`, `canvas`, `portrait`, `backdrop`, `cover` | Where it may appear. Only `of-the-time` and `place-today` stand for an entity on the canvas; a later imagining only on its card; a generated picture never on a person or an object | built |
| `category`, `attestation` | Made: always `imaginative` and *imagined*. Found: absent; the class says what it is | Badge on a made picture, never hidden | specified |
| `groundedIn[]` | Made: the passages the prompt was built from, as shape 3 quotes (`informedBy`, today plain lines) | "Built from" row: what the picture rests on | partly built |
| `avoided[]` | Made: what the prompt kept out (faces, flags and emblems, lettering, modern objects) | Shown to scholar and student | built |
| `generator` | `{provider, model, version}` (`model`) | Quiet footer | built |
| `prompt`, `promptHash` | The prompt used, and its hash | Shown to scholar and student; hidden for browser | prompt built |
| `supersedes`, `derivedFrom` | The picture this one replaces; the still a 3D model was made from | A chain under the viewer | supersedes built |
| `credit`, `licence` | Found: author, date, licence, attribution required. Made: `{terms, commercialUse, checkedAt}` from the provider when made | Footer; blocks export if not free for commercial use (public domain first) | found built |
| `status` | `proposed`, `accepted`, `rejected` (`review`: "awaiting the curator") | Dashed frame and "awaiting review" while proposed | built |
| `createdBy`, `createdAt`, `approvedBy` | Who asked, when (`made`), who accepted | Review history, collapsed | partly built |

Example (the backdrop in use, trimmed):

```json
{
  "kind": "image",
  "origin": "made",
  "class": "generated",
  "depicts": ["chr:entity:battle-of-actium"],
  "use": "backdrop",
  "category": "imaginative",
  "attestation": "imagined",
  "groundedIn": [{ "accordingTo": "Plutarch, Life of Antony", "locator": "Plutarch, Antony 64-66",
                   "quotation": "<the passage on the large, slow ships and the light, quick ones>" }],
  "avoided": ["faces", "flags and emblems", "lettering", "modern objects"],
  "generator": { "provider": "Figma", "model": "gpt-image-2.5-flare" },
  "supersedes": "actium-backdrop-1.png",
  "status": "proposed"
}
```

Its caption reads: *Illustration, generated: not a picture of the battle;
awaiting the curator's review.* A made picture of a subject sits in the "How it
is read" part of the card (D-124), as an illustration of a source's
description, never above the evidence. For example, Hale's "the state galley of
Cleopatra, a floating palace" (Hale 2.12) could ground a still of the galley.

## 5. Shape 9 — A generation step and its progress (specified)

A request that costs money is a **step of the inquiry's plan** (31 §5; D-174):
it carries its action, target, rationale, `budget_usd` and decision like any
other item, and the guided orchestrator (D-175) runs it once approved, within a
named budget and the per-item cap. There is no separate job system (agreed
with the orchestrator, D-175). What this addendum adds is one action, the
workers, and what the drawer shows.

**The item** (`PlanItem`, `orchestration/contracts.py`):

| Field | Meaning |
|---|---|
| `item_id` | The plan item (P07) |
| `action` | `GENERATE`: one action for every kind; the kind (`scene-movement`, `scene-flyby`, `image`, `model3d`, `video`) is in the worker's arguments. A new value of the closed `PlanAction`, added when the first worker is built |
| `target` | The entity the scene or picture is about |
| `rationale`, `expected_outputs` | Why, and what it gives ("a still of the galley, proposed", "a movement spec, proposed") |
| `budget_usd` | The estimate, shown before any decision; words beside it: "3 images" |
| `depends_on` | For a model: the item that makes its still |
| `decision` | `awaiting`, `approved`, `rejected`, `modified`, `deferred`; each decision is a new plan version |

**The worker call** (`<run>.calls.json`): `{worker, arguments}`, a
`python -m` module that exits non-zero on failure. The orchestrator runs it with
`CHRYSTALLUM_RUN=<run>:<item>`, and for a paid item with `CHRYSTALLUM_BUDGET`
and `CHRYSTALLUM_RUN_CAP` (1.5 times the estimate). A media worker must spend
through `spend_meter` (or write ledger lines under that run name), or its cost
is not seen and the cap does not hold.

**The result** (`WorkerResult`): `status`, `outputs` (file paths: the
picture, its shape 8 record, or the shape 7 spec), `proposal_ids`, `cost_usd`,
`error`. An `error` is shown in plain words, never a provider's raw message.

**The pause before a model** is two items: P07 makes the still, P08 makes the
3D model and depends on P07. P08 stays awaiting until the reader has seen the
still and approved P08, so a bad picture does not become a bad model, with no
special state.

**What the drawer shows** is read from the run file: an item `running` (its
assignment has no result yet), `done` with its outputs, `failed`, or
`set_aside` (a failed attempt kept on record). The orchestrator runs items one
at a time in the foreground, so a live progress bar inside a step is not
available yet; the drawer shows the step's state only. The Plan view
(wireframe) shows a media step with Approve, Reject and Defer like any other.

**Where the items come from.** The front door plans from
`curation/recipes.json` only. A media command (`picture Actium`) needs a small
builder that adds its item to the current plan as a new version; or a recipe
entry, for media a recipe should always propose. Not built.

## 6. Node card — additions

Four fields on shape 4 (26 §4):

| Field | Meaning | State |
|---|---|---|
| `pictures[]` | Shape 8 records that depict this entity: of the time first, then the place today, a reconstruction, a map, a later imagining, a generated one last. The card shows four, "All N pictures" opens the rest | built (wireframe, `gallery`) |
| `cover` | For a group (D-173): the picture or view that opens it (the Participants poster) | built (wireframe) |
| `scenes[]` | `{type, id, status, legs}` for each scene the entity is the subject of or a unit in | specified |
| `movementLegs` | How many accepted legs it has, by `basis`: `{sourced, inferred}`; shown as "Moves in 2 scenes" | specified |

## 7. Persona and the imagined switch

Generated pictures and illustrative legs are imagined, so they follow the rule
for fiction in 26: one switch, the persona sets the default. Found pictures are
not imagined (a later imagining is labelled by its class) and are always shown.

| Persona | Made pictures | Prompt and generator | `inferred` legs | `illustrative` legs |
|---|---|---|---|---|
| browser | on | hidden | shown, dashed | shown, faded |
| student | off until switched on | shown | shown, dashed | hidden |
| scholar | off until switched on | shown | shown, dashed | hidden |

The poster's backdrop is the exception that proves the rule: it is shown in
every persona because it is labelled on the stage itself ("Illustration,
generated: not a picture of the battle") and carries no positions.

A persona changes what is shown and never what is stored or accepted.

## 8. Messy cases to design for

Real or already seen in the graph.

1. **A unit with no place.** The claims say who commanded a wing, not where it
   was (26 §1, D-128). Its leg cannot be drawn as a line; list it in the
   footnote and show it by name, dashed.
2. **A Place with no coordinates.** 4 of the 26 Places in the export have none.
   They go to the "Not on the map" tray (26 §4); a leg that ends there is a
   label, never a guessed point.
3. **Sources that disagree about the move.** Two voices put the same unit in
   different places. Draw both as `alternatives`, each with its voices, and
   let the reader choose which to follow; never choose for them.
4. **Almost no dates.** Most legs have `timeWords` only, and the scrubber steps
   by phase. The undated tray stays.
5. **The wrong name for the time.** Octavian is stored as "Augustus" (26 §7,
   case 4). Prompts and captions must use the name he bore in the scene's year,
   or the picture will say Augustus at Actium (§1, principle 7).
6. **Modern terrain.** Hosted terrain is modern. Show the caption on every
   flyby, and never place a ship on ground that was sea in 31 BC, or at sea
   where there was land, without it (§11, question 5).
7. **A face.** A generated picture of a real person is invention. Made pictures
   show scenes, ships, places and objects; a person's likeness comes only from
   a found picture of their time (a coin, a bust), labelled so.
8. **A failed or poor generation.** Show the error in words, keep the prompt,
   and offer "try again" and "edit prompt" for scholar; browser sees only
   "try again". A rejected record stays in the audit, not on the card; a
   replaced one is linked by `supersedes`.
9. **A proposed entity in a scene.** Most entities are still proposed (688 of
   892 in the export). Draw them, marked, as in 26 §7 case 6; never leave them
   out of a scene.
10. **The licence changes.** A provider's terms are recorded when the file is
    made (`licence.checkedAt`). A file not free for commercial use is shown but
    not exported (public domain and CC0 first).
11. **A found picture that is not what it seems.** A plaster cast or a modern
    copy described as a statue of the time. The class `reconstruction` catches
    the words Commons uses; anything uncertain is `doubtful` and goes to the
    review list, not the card.

## 9. Visual encoding — additions to 26 §8

| Data | Values | Suggested encoding |
|---|---|---|
| Leg `basis` | sourced, inferred, illustrative | Solid, dashed ("our line"), faded |
| Leg or spec `status` | proposed | Dashed frame on the stage, as for entities |
| Unit `side` | from the order of battle | The side's colour; `null` is neutral grey |
| Picture `class` | of the time … generated | The caption's first words; a made picture also carries the *imagined* badge |
| Picture `kind` | image, model3d, video | Small mark on the viewer: still, cube, clip |
| Item state | awaiting, running, done, failed, set aside | Chip in the drawer and on the Plan view; *waiting* uses the signpost style, since it needs the reader |

## 10. How it is built (not part of the contract)

The shapes above hold whatever sits behind them. For reference:

- **Built:** found pictures through `adapters/commons_images.py` (Commons
  descriptions, classes, licences; Wikipedia articles listed in
  `curation/wikipedia-articles.json`); generated pictures by hand through Figma's
  image generator, each with its JSON record; both embedded in the wireframe by
  `build.py`.
- **Requests:** the front door (D-174) and the guided orchestrator (D-175). A
  scene step calls Claude through the API with tool use, reading cards, notes,
  the order of battle and Place coordinates, and returns a scene spec as a
  Proposal.
- **Generation:** one gateway behind an adapter (a hosted aggregator, or Figma
  as today), so providers can change without changing these shapes. Image
  models for stills; an image-to-3D service producing GLB; a video model for
  clips only. Results are stored by hash of the spec.
- **Rendering:** MapLibre with deck.gl for Movement; CesiumJS with hosted
  terrain for Flyby; `<model-viewer>` for Model; Cytoscape for the graph and the
  poster.
- **Provenance:** each picture record is written to the graph with `DEPICTS`
  edges and `groundedIn` passage links (images themselves never go into Neo4j,
  D-096); each spec is held as a Proposal.

## 11. Decided, and open questions for the curator

Decided in this revision (D-176):

- Inferred and illustrative movement are Generalized Abstractions (D-172):
  drawn and labelled, never stored as claims. Illustrative legs are allowed,
  under that label.
- Paid requests are plan items with the action `GENERATE`, approved and
  budgeted like any other, run by the guided orchestrator, spending through the
  meter (D-174, D-175).
- Movement is the Animation view on the Map, not a new mode.
- Video is not in the first release.

Open:

1. **Do accepted sourced legs become facts?** This draft says yes, with a
   "moved to" style predicate so they appear on the unit's card with voices.
   The curator to confirm and to name the predicate.
2. **Who may accept a scene or a picture?** The same people who accept
   Proposals, or a lighter step for imagery.
3. **How a media command reaches the plan:** a small builder that adds the
   item to the current plan (a new version), or a recipe entry. The action is
   `GENERATE` (agreed with D-175).
4. **An ancient coastline.** At Actium the shore decides where a ship could
   be. Is an ancient surface (from the gazetteer, 27, or a held basemap) worth
   building before Flyby, so `terrain.source` can be `ancient`?
5. **Colour by kind** is still undecided (26 §8); pictures and scenes will need
   a place in it.
