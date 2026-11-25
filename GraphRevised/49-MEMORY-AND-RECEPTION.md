---
status: decided 2026-11-25 (D-180): registry v22 holds commemorates and depicts; objects of their own time are Objects; reconstructions are links only
authority: curator, 2026-11-25 (chat): propose commemorates and depicts, after a review of Actium artwork; the storyboard's memory segment (26a §5a, D-179) needs them
depends_on: [02-GRAPH-MODEL.md, 26a-UI-DATA-CONTRACT-SCENES.md, 44-HISTORIOGRAPHY-AND-DEBATES.md, 45-NATURAL-KINDS-AND-MATERIALS.md]
superseded_by: null
last_reviewed: 2026-11-25
---

# 49 — Memory and Reception: what commemorates an event, and what depicts it

**For:** the curator, and the session that keeps the predicate registry.
**Status:** decided (D-180). Registry v22 holds both predicates, and the graph is synced (registry nodes, graph type). No objects are entered yet; §5 is how they will be.

## 1. Why

An event lives on after it happens, in two ways the graph cannot yet say:

- **The objects its own time made to remember it.** Coins and gems, a victory
  monument, a dedication, a relief. They are evidence, but of how the event
  was remembered and used, not of what happened in it. A coin cannot place a
  ship; it shows how the victors wanted the victory seen.
- **The works later ages made of it.** Paintings, tapestries, plays. They are
  reception: what later ages imagined. They are never evidence about the
  event itself.

The storyboard specialist found this gap on its own. For the Battle of
Actium's last phase, "meaning and memory", it could propose nothing richer
than a timeline: commemorations 0, depictions 0 (storyboards/battle-of-actium.storyboard.json).
This is also the historical-thinking focus: how an event was remembered and
reimagined is content, not decoration.

## 2. Three roles, kept apart

| Role | Examples (Actium) | What it is | In the graph |
|---|---|---|---|
| **1. Remembered in its own time** | coins with victory types, the victory monument at Nicopolis, the Actian games, a dedication | Evidence of memory and of its political use | An entity, with `commemorates` to the event |
| **2. Reimagined later** | a 17th-century painting of the battle, a tapestry of the story | Reception, an imaginative work | A Work of a creative form, with `depicts` to the event; kept in the imaginative category |
| **3. Modern reconstructions** | illustrators' plates, 3D reconstructions, video | Mostly copyrighted | Not stored. A link only, as a reference for curators |

## 3. The two predicates (drafts for the registry)

```json
{"id": "commemorates", "display": "commemorates",
 "definition": "An object, work or institution was made or founded to remember an event or a person: a coin type, a monument, a dedication, games. Asserted when the thing says so itself (its legend, its inscription); attributed when a source or a scholar reads it so. Evidence of how the event was remembered and used, never of what happened in it.",
 "subjectKinds": ["Object", "Work", "Place", "Event"], "objectKinds": ["Event", "Person"],
 "symmetric": false, "category": "interpretive",
 "qualifiers": {"context": "none", "role": "none", "time": "optional"},
 "modes": ["asserted", "attributed"], "wikidata": [{"pid": "P547", "direction": "forward"}]}
```

```json
{"id": "depicts", "display": "depicts",
 "definition": "A work shows an event, a person or a place: a painting of a battle, a relief, a scene in a play. Says what the work shows, not that it shows it truly; a work of a creative form stays an imaginative work.",
 "subjectKinds": ["Work", "Object"], "objectKinds": ["Event", "Person", "Place"],
 "symmetric": false, "category": "interpretive",
 "qualifiers": {"context": "none", "role": "none", "time": "none"},
 "modes": ["asserted", "attributed"], "wikidata": [{"pid": "P180", "direction": "forward"}]}
```

The two Wikidata properties were checked at Wikidata on 2026-11-25:
P547, *commemorates* ("what or whom is commemorated by the place, monument,
memorial, or holiday"); P180, *depicts* ("entity visually depicted in an
image, literarily described in a work…").

**Why both are interpretive.** Whether an object was *meant* to remember an
event is a reading of intent. The legend can make it plain; often a scholar
supplies it. For example, whether the Medinaceli reliefs show Actium is a
scholar's reading, and an open Question.

## 4. A snag in the registry: a relief is not fiction

`creativeForms` holds `painting` and `sculpture`. Any Work of those forms is
treated as imaginative (a separate category, never history). That is right
for a 17th-century painting. It is wrong for an Augustan relief, which is a
source made in its own time.

Two ways out, for the curator:

- **(a)** Model objects of the time as **Object** (a monument, a relief, a
  gem), not as Works of a creative form. Only later art is a Work of a
  creative form. Nothing in the registry changes.
- **(b)** Add an era test: a Work of a creative form made within the event's
  own time is a source, not an imaginative work. This would mean changing
  the rule that reads `creativeForms`.

I recommend **(a)**: simpler, and it matches what the things are. A coinage
is already a Work of form `coinage`, which is not creative, so coins are
unaffected.

## 5. How it is filled

The storyboard's gaps for the memory segment become plan items through the
orchestrator's `extend`:

- coins commemorating the victory: Nomisma and OCRE (already REGISTER items
  in the Actium plan), or CRRO;
- the Nicopolis monument and its dedication: the published record, and
  epigraphic databases;
- later works: museum records and Wikimedia Commons, public domain first.

Each object enters as a proposed entity, with its *commemorates* or *depicts*
link proposed and its source quoted. The pictures go in as shape 8 records:
an object made at the time is classed `of-the-time`; a later work is a
`later-imagining`. Once the facts exist, the memory segment qualifies for
`memory-reception` and the scene can gain a closing step, "How it was
remembered".

## 6. Decided (curator, 2026-11-25; D-180)

1. `commemorates` and `depicts` are adopted as drafted, in registry v22.
2. Objects of their own time are modelled as **Object** (§4 a). `creativeForms` is unchanged.
3. Modern reconstructions are kept as links only, never stored.
