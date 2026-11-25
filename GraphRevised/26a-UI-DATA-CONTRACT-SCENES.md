---
status: draft
authority: what the explorer receives for movement, flybys, and pictures found or made (shapes 7 to 9)
depends_on: [26-UI-DATA-CONTRACT.md, 02-GRAPH-MODEL.md, 29-EVENT-CENTRED-INQUIRY.md, 31-ONE-COMMAND.md, 32-RESEARCH-WORKSPACE.md]
implemented_by: [adapters/commons_images.py (pictures found), explorer/images/generated/*.json (pictures made), scenes/actium_campaign_31bc.py (the first scene), explorer/wireframes/build.py (gallery, backdrops, scenes)]
superseded_by: null
last_reviewed: 2026-11-24
---

# 26a — Scenes, pictures and generated media (addendum to 26)

**Date:** 2026-11-24 (D-176). **For:** the curator designing the stage modes,
and whoever builds the read API, the orchestrator's generation steps, and the
renderers. **Status:** pictures found (Commons and Wikipedia) and one generated
backdrop are built and shown in the wireframe, and so is the first movement scene
(Actium, §3, drawn in the Animation view); flyby, the 3D model and video are
specified here and not built. Shapes 7, 8 and 9 are new; the node card
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
| **Movement** | The Animation view, switched from Phases to Scene, taking the whole centre | Units moving between places step by step, on a campaign map and a battle map, each step's statements with their basis and passages beside it | Shape 7, `type: movement` | built (wireframe: the Actium scene) |
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

## 3. Shape 7 — Scene spec: a plan the renderers draw (built for Actium)

One spec per scene, held as a file in `scenes/` (a Proposal once the graph can hold one, §10).
The first is the Actium campaign, `scenes/actium-campaign-31bc.proposed.json`. Its builder is
`scenes/actium_campaign_31bc.py`, and the wireframe's Animation view draws it (§2).

The rule the shape enforces: **every sentence and every line says what it rests on.**
- A sentence is a passage quoted verbatim with its locator, or an inference with its author, or
  a statement not yet checked, with who asserted it.
- A line is a sourced move, our join between sourced points, or a drawing with no source.

The builder reads each quotation from the stored passage and stops if it is not a verbatim
substring.

**The scene:**

| Field | Meaning | Design use |
|---|---|---|
| `id` | `chr:scene:<slug>`; later a hash of the content, so the same request returns the same result | Never shown |
| `type` | `movement` or `flyby` | Which mode opens |
| `subject` | The entity the scene is about (`id`, `label`, `kind`) | Stage title |
| `scope` | What the scene covers, in words, when it runs beyond the subject (a campaign around a battle) | Under the title |
| `sequenceBy` | `order` (the scene's own steps), `phase` (D-091), or `time` (only where every step has dated terms) | How the scrubber steps |
| `status` | `proposed` or `accepted`; the scene as a whole | Badge, dashed frame |
| `proposedBy`, `proposedAt` | Who drafted it, and when | Review note |
| `derivedFrom` | Where it came from: `file` (a source animation), `madeBy` (who made that, and from what), `note` (what that origin means for trust), `check` (the check document), `builtBy` (the builder) | "Where this scene comes from" |
| `bases` | The basis words, defined in the scene itself | Legend |
| `layers[]` | `terrain`, `places`, `unitPaths`, `labels`, `orderOfBattle` | Layer switches |
| `terrain` | `{source, note}`: `modern`, or `ancient` when an ancient coastline is held (§11). The note carries the basemap's licences | Caption on the map |
| `places` | The places the scene names, by key (below) | Pins and labels |
| `steps[]` | The scene in order (below) | The animation |
| `camera` | For `flyby`: `{path: [{at, target, altitude, heading, pitch}], duration, followLegs}` | The camera script |
| `footnote` | What the scene leaves out, what is not held, what was added for it | Footnote on the stage |

**A place:**

| Field | Meaning |
|---|---|
| `label` | The name of the time (Patrae, Corcyra), not the held label |
| `entity` | The Place entity, when held; `heldAs` its label when that differs (Patras, Corfu); `status` the entity's |
| `lonLat`, `lonLatFrom` | The point, and where it comes from: the place's card (its Pleiades or GeoNames Location), or a source animation (unverified) |
| `held` | `false` when the graph has no entity yet; the place goes to the gazetteer as a proposal |

**A step:**

| Field | Meaning |
|---|---|
| `order`, `title`, `timeWords` | Its place in the scene, its title, the sources' own time words |
| `phase` or `context` | The event's phase (D-091), or, outside the event, what it belongs to ("after the battle") |
| `view` | `overview` (the campaign map) or `battle` (the battle-area map) |
| `statements[]` | What the step says, sentence by sentence (below) |
| `legs[]` | Moves between places (below) |
| `placements[]` | Positions within the step: a unit as a line `[[lon, lat], [lon, lat]]`, with `basis` and `note`. No passage gives a ship's position, so at Actium every placement is `illustrative` |
| `ordersOfBattle`, `routes` | Disagreements between sources, kept side by side and never merged: `{note, alternatives: [{accordingTo, words or the order, voices, note}]}` |
| `disputed` | `{words, questions}`: the graph's debated Questions the step touches |
| `corrected[]` | What the source animation said that the passages contradict or reorder: `{was, why, voices}` |
| `locatorNote` | When the source cited another edition's numbering, how it maps to the text held |
| `army` | A unit that does not move but changes (an army that goes over), at its place |

**A statement:**

| Field | Meaning |
|---|---|
| `text` | One sentence, in our words |
| `basis` | `sourced`, `inferred`, `illustrative` or `not-checked` (below) |
| `voices[]` | For `sourced`: each passage, as `accordingTo`, `work`, `observation` (the stored passage), `locator`, `url`, and `quotation`, verbatim |
| `by` | For `inferred`: whose inference. For `not-checked`: who asserted it |
| `note` | What the reader should know: a conversion ("eight furlongs, some 1.5 km"), a narrower reading, where two sources part |

**A leg** (one move of one unit):

| Field | Meaning |
|---|---|
| `unit` | `{entity, label, side, heldAs}`: the label is the name of the time ("Octavian", held as "Augustus") |
| `from`, `to`, `via[]` | Places (above). A place with no point goes in the "Not on the map" tray, and its leg is drawn as a label, not a line |
| `basis` | As for a statement; a line between sourced places is `inferred` unless a passage states the route |
| `accordingTo` | When the leg is one source's version (two routes for Cleopatra) |
| `note` | What is sourced and what is ours ("each place is sourced; the line between them is ours") |
| `status` | `proposed`, `accepted`, `rejected` (audit only) |

`basis` values:

- **sourced:** a stored passage says it; the quotation is verbatim. A sentence is drawn plain with
  its passages under it; a move is drawn solid. An accepted sourced move between named places
  is also a fact (shape 2), so it appears on the unit's card. The predicate is the curator's
  to name (§11, question 1).
- **inferred** (a Generalized Abstraction): joined up from sourced points, such as the path
  between two places, their order, or a compass point. Drawn dashed; `by` names whose
  inference it is. Never stored as a claim.
- **illustrative** (a Generalized Abstraction): no passage, drawn so the picture reads (a fleet's
  line on the water). Drawn faded, with a caption saying so. Hidden when the persona is
  scholar or student and "imagined" is off (§7).
- **not-checked:** it rests on a passage not held yet, or on none. Shown with who asserted it,
  and never drawn as a line. Reading the passage (extraction) moves it to sourced or inferred,
  or to `corrected`. At Actium, only the date of Alexandria's fall remains: no passage held
  gives it.

Example: one step of the Actium scene, trimmed.

```json
{
  "order": 6, "phase": "engagement", "view": "battle",
  "timeWords": "the sixth hour (about midday)",
  "title": "Antony's left wing moves first",
  "statements": [{
    "text": "At the sixth hour, with a wind rising from the sea, Antony's men put their left wing in motion.",
    "basis": "sourced",
    "voices": [{
      "accordingTo": "Plutarch, Life of Antony",
      "observation": "chr:observation:perseus:tlg0007.tlg058.perseus-eng2:65.4:70427323",
      "locator": "Plutarch Antony 65.4",
      "quotation": "it was now the sixth hour, and since a wind was rising from the sea, the soldiers of Antony became impatient at the delay"
    }]
  }],
  "placements": [{
    "unit": { "entity": "chr:entity:antony-fleet-at-actium-left-wing", "label": "Left wing of Antony's fleet", "side": "Antony" },
    "line": [[20.722, 38.921], [20.733, 38.905]],
    "basis": "illustrative",
    "note": "Positions drawn; the movement itself is sourced (Plutarch 65.4-5)."
  }]
}
```

**What a source animation becomes.** The Actium scene began as an animation that Claude made
in a chat, from Wikipedia and its own knowledge. Its locators were claimed, not read. It was
checked step by step against the stored passages, and the passages it needed were read.
What stood became `sourced`, what was joined up `inferred`, and the ship lines `illustrative`.
What the passages contradicted went to `corrected`, and where the sources disagree, both
versions are kept. Any made thing can come in this way, provided its evidence can be traced
(curator, 2026-11-24).

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
| `id`, `kind` | `image`, `model3d`, `video`, or `audio` (a voiced narration: one record per scene, persona and voice, its clips listed; see `scenes/NARRATION.md` and D-178) | Which viewer or player | image and audio built |
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

## 5a. Shape 10 — Storyboard: which presentation for which stretch (draft, 2026-11-25)

**Status:** adopted (D-179, 2026-11-25) and built. `GENERATE` has its first worker, the general scene builder (D-181, below):
- the specialist and its check, `narrative/storyboard.py`;
- the catalogue, `curation/presentations.json`;
- the `STORYBOARD` action and its recipe step;
- the Storyboard view in the wireframe.

The first run is `storyboards/battle-of-actium.storyboard.json`. The
hand-worked example it was modelled on is `scenes/actium-campaign-31bc.storyboard.json`.

A **storyboard specialist** walks an inquiry's timeline and proposes, for each
stretch, which presentation to use. It owns **choices of form only**: no facts,
Questions, predicates or sources (unlike the lens specialists, D-137). If a
form needs something the graph lacks, the specialist files a gap; it never
writes the fact. The same rule as the rest of this addendum: the agent writes a
plan, never a fact.

**How it works:**

1. **Catalogue.** Each presentation kind states:
   - what question it answers;
   - what an evidence profile must show for it to fit (`needs`);
   - what it must never imply (`never`);
   - whether it is built.

   The `never` column carries the provenance rules into the choice of form. A
   movement scene never implies the route; a battle scene never implies where
   ships stood; a disagreement view never picks a winner.
2. **Profile.** Code computes a profile for each stretch from the graph:
   - statements by basis;
   - time grain, located places and the extent between them;
   - movements, units and phases;
   - alternatives, disputes and corrections;
   - commemorations and depictions;
   - pictures by class.

   The model reads the profile; it never writes it. **Grain and extent pick most
   views:** hours within 50 km give a close map, months over hundreds of km give
   a campaign map, and decades give a timeline.
3. **Proposal.** For each segment the specialist gives:
   - the kind, and any kinds shown with it (`with`);
   - **why**, as profile values against the catalogue's conditions;
   - the transition from the last segment: zoom in, zoom out, or cut;
   - the **gaps**, each becoming a Question, a source task or nothing.
4. **Check.** Code checks every segment's kind against its profile, as
   `narration_check.py` does for narrations. Examples it rejects:
   - a movement scene with one located place;
   - an order of battle that merges two sources;
   - a kind whose `needs` the profile does not meet.
5. **Review.** The curator reads the reasons and the gaps, and approves or
   vetoes segments: a review of reasoning, not of output. Each approved segment
   becomes a `GENERATE` plan item (§5) for the builders already in place: the
   scene builder, the narration and its check, the voice (D-178).

**The record:**

| Field | Meaning |
|---|---|
| `id`, `subject`, `scope`, `persona` | What is storyboarded, for whom. The persona changes how a kind is shown, not which kinds fit |
| `catalogueVersion` | The catalogue the choices were checked against |
| `segments[].span` | The stretch: time words, events, or scene steps |
| `segments[].profile` | The computed evidence profile (step 2) |
| `segments[].kind`, `with` | The chosen presentation, and any shown with it (order of battle, disagreement) |
| `segments[].why` | The reasons, each a profile value against a condition |
| `segments[].transition` | How the stage moves from the last segment |
| `segments[].gaps[]` | `{what, becomes: question \| source-task \| none, note}` |
| `segments[].status` | proposed, approved, vetoed, built |
| `overlays[]` | Narration and other layers over segments |
| `check` | `{problems, warnings}` from the code check |

**The worked example, Actium.** Four segments:
1. **The campaign, steps 1–4:** a movement scene. Grain of months, 536 km, 5 legs.
2. **The battle, steps 5–11:** a battle scene, zooming in, shown with the orders
   of battle and the disagreements. Grain of hours, 12 km, 6 phases, 8 units.
3. **The flight and the end, steps 12–13:** a movement scene, zooming out. 1,197 km,
   with the two routes.
4. **How it was remembered:** a memory and reception segment, proposed. It
   qualifies on nothing yet; its gaps are the coins (Nomisma, OCRE), the Nicopolis
   monument, the open reading of the Medinaceli reliefs, and the later paintings.

The narration (D-178) is an overlay on segments 1–3.

**Agreed with the orchestration session (2026-11-25), adopted by the curator (D-179):**

- **Two new actions, D-179 reserved for them.** `STORYBOARD` (the specialist)
  and `GENERATE` (one action for every kind, the kind in the worker's
  arguments). Each is added to the closed `PlanAction` only in the same
  commit as its first worker, with a contract test.
- **Planning.** A recipe entry, `STORYBOARD`, runs after `PHASES` when the
  inquiry has phases, so the front door proposes it like any other item.
- **Approved segments join the plan.** The orchestrator's `extend_plan(state,
  items, by, source)` adds them as a new plan version (the old one kept); it is
  owned by the orchestration session. New items arrive awaiting, so plan
  approval stays the gate.
- **The item shape.** Per segment, a `GENERATE` item:
  - target, rationale (the segment's reasons), expected outputs, budget;
  - a `call`: worker and arguments;
  - an `origin`: storyboard, segment, and gap if any; kept on the item's call in `<run>.calls.json`.
- **Gaps go through the same path,** not through the brief's ranking:
  - a candidate source becomes `REGISTER`;
  - a registered source not yet in the inquiry becomes `SOURCE_PLAN`;
  - a source already in the inquiry becomes `FIND` then `READ`;
  - a source that already has an item is skipped;
  - a question gap becomes a proposed Question.

**Open:**

- a battle scene from passages (its ship lines are a Generalized Abstraction the curator draws), flyby and memory-reception: `GENERATE` draws only `scene-movement` so far (D-181);
- the profile does not yet count the pictures held;
- the memory and reception layer (`commemorates`, `depicts`), proposed in doc 49, needed before the memory segment can qualify.

### The general scene builder (D-181)

`scenes/build_scene.py` is `GENERATE`'s first worker. It draws a storyboard
segment as a movement scene (shape 7) from the passages the graph holds.

1. **Evidence, by code.** It gathers:
   - the segment's phases;
   - the events placed in them;
   - the passages that depict those events, with their stored text and locators (the most-cited first, about 90,000 characters at most);
   - the located places those passages name, with gazetteer points and names;
   - the people and groups who took part.
2. **Draft, by the model.** Steps by phase, each with:
   - statements, sourced by verbatim quotations or marked inferred with a note;
   - legs between listed places only;
   - disagreements as two versions.

   Ancient witnesses are preferred; a modern author quoted is named in the statement.
3. **Check, by code**, with one repair round. It requires that:
   - every quotation is word for word in its passage;
   - a sourced statement has a quotation, and every number it states is in it;
   - legs run between listed places, for listed units;
   - a sourced leg's statement quotes a passage naming both ends;
   - steps keep the phases' order.
4. **Assembly.** A place takes the name the quoted passages use most (Corcyra,
   not Corfu); the held label is kept as `heldAs`. Statement ids follow the
   shape-7 pattern, and the scene carries a `contentHash`. A basemap is taken
   from a held page whose map holds every point. A narration input is written
   beside the scene, so narration and voice (D-178) work unchanged.
5. **Kept.** The model's draft is saved as `<scene>.draft.json`;
   `--from-draft` re-checks and re-assembles it after a code fix without
   asking the model again.

**The first run.** Actium, segment 1 (the road to war and the isolation):
- 54 passages in, 8 steps out, 20 statements, all sourced, 12 legs;
- passed after one repair round, for $0.55;
- it adds the gathering at Ephesus and the moves by Samos to Athens, which the hand-built scene lacks;
- it keeps two real disagreements: Dio against Weigall on Corcyra, and Dio and Velleius against Wikipedia on who took Patrae.

The wireframe shows it beside the hand-built scene; a chooser in the
Animation head switches between them.

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
| Statement `basis` | sourced, inferred, not-checked | A chip before each sentence: filled, dashed, dotted; a sourced sentence has its quotations under it, the others say whose it is |
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
- Movement is the Animation view on the Map, not a new mode: a switch between
  Phases and Scene.
- A scene speaks sentence by sentence, each with its basis (`sourced`, `inferred`,
  `illustrative`, `not-checked`); sources that disagree are kept as alternatives;
  what a source animation said and the passages contradict is kept as `corrected`
  (§3).
- A made animation is welcome as a source of a scene, when its evidence can be
  traced: it is checked against the stored passages first (curator, 2026-11-24).
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
