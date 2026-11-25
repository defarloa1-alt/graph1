# Narrating a Chrystallum scene: what the narration is keyed to

**For:** the app or model that writes the narration (spoken or captioned) for a movement scene.
**The scene it narrates:** `actium-campaign-31bc.narration-input.json` in this folder. It holds only the fields in §2: the scene without its map coordinates, which are never narrated. The full scene is `actium-campaign-31bc.proposed.json`, whose shape is defined in `26a-UI-DATA-CONTRACT-SCENES.md` §3. Both files are written together by `actium_campaign_31bc.py`, so their ids and `contentHash` always match. The scene is played as an animation of 13 steps, on a campaign map and a battle map.

Chrystallum is a history graph with strict provenance. Every sentence in a scene says what it rests on, and the narration must keep that promise: **the narration may only say what a statement says, worded according to its basis.**

## 1. What to key to

Narrate the scene **step by step and statement by statement**, never by clock time.

| Key | Looks like | What it is |
|---|---|---|
| Scene | `id: chr:scene:actium-campaign-31bc` with `contentHash` | The scene, and the exact version you narrated |
| Step | `steps[].id`, e.g. `chr:scene:actium-campaign-31bc#6` | One screen of the animation: a map view, a title, its statements |
| Statement | `steps[].statements[].id`, e.g. `…#6.1` | One sentence, with its basis and its passages |

Every narration line names the statement(s) it voices. Lines can also voice four other parts of a step, keyed as follows:
- a step's two versions of an order of battle: `<step id>:ordersOfBattle`;
- its two routes: `<step id>:routes`;
- its open debate: `<step id>:disputed`;
- its correction: `<step id>:corrected`.

A line that voices nothing may only be a transition with no claim in it ("Now to the battle itself."). The check (`narrative/narration_check.py`) rejects any other unkeyed line.

## 2. Read these fields

From the scene:
- `id`, `contentHash`, `scope`, `subject.label`.

From each step:
- `id`, `order`, `title`, `timeWords`, `view` (`overview` or `battle`), `phase` or `context`.
- `statements[]`:
  - `id`, `text`, `basis`;
  - `voices[]`, each with `accordingTo`, `locator` and `quotation`;
  - `by`, `note`.
- `ordersOfBattle`, `routes`: two sources that disagree, each with its own voices.
- `disputed`: `{words, questions}`, an open debate.
- `corrected[]`: something the original animation said that the passages contradict.

Ignore `legs`, `placements` and `places`. They draw the map, and the map is not the narrator's to describe as fact (§3, rule 4).

## 3. The rules

1. **Say nothing that is not in a statement.** No new names, numbers, dates, motives or places. If the scene doesn't say it, the narration doesn't either.
2. **Word each line by its statement's basis:**

   | basis | How to say it | Example |
   |---|---|---|
   | `sourced` | As the source tells it. Name the source when it matters, and always where sources disagree | "Plutarch tells us that at the sixth hour, as a wind rose from the sea, Antony's left wing began to move." |
   | `inferred` | As a reading, not a fact: "we have drawn", "it seems", "most likely" | "From there he probably marched south to his camp; the sources give the places, not the road." |
   | `not-checked` | Leave it out, or say plainly that it isn't in the sources held | "The city fell, by the usual account, on the first of August; no passage we hold gives the date." |

3. **Quote only verbatim.** You may read a `quotation` aloud, word for word, and attribute it ("in Perrin's translation of Plutarch…"). Never change words inside quotation marks; paraphrase outside them.
4. **The map's positions are drawn, not sourced.** Never narrate where ships stood as fact. If you mention the picture at all, say what it is: "The lines on the map are drawn to orient you; no ancient writer gives the ships' positions."
5. **Where sources disagree, voice both.** For `ordersOfBattle` and `routes`, attribute each version and never choose between them: "Plutarch puts Agrippa on the left; Velleius gives the left to Arruntius."
6. **Debates stay open.** For `disputed`, present the question, not an answer: "Did Cleopatra plan her escape before the battle? Historians still disagree."
7. **Corrections are not narrated as fact.** A `corrected[].was` sentence is false by the passages. Leave it out, or narrate the correction: "the money stayed aboard the ships left fighting."
8. **Names of the time:** Octavian, never Augustus, before 27 BC. Corcyra, Patrae and Leucas, as the scene's statements have them.
9. **Tone:** plain and vivid, short sentences, no superlatives that the sources don't give.

## 4. What to return

One JSON file per scene version:

```json
{
  "sceneId": "chr:scene:actium-campaign-31bc",
  "sceneContentHash": "<the scene's contentHash>",
  "language": "en",
  "persona": "browser",
  "madeBy": "<app and model>",
  "madeAt": "<ISO date>",
  "steps": [
    {
      "stepId": "chr:scene:actium-campaign-31bc#6",
      "lines": [
        {
          "id": "n6.1",
          "kind": "narration",
          "text": "Plutarch tells us that at the sixth hour, as a wind rose from the sea, Antony's left wing began to move.",
          "keys": ["chr:scene:actium-campaign-31bc#6.1"],
          "basis": "sourced",
          "estSeconds": 6.5
        },
        {
          "id": "n6.2",
          "kind": "narration",
          "text": "Octavian ordered his right wing to row backwards, to draw the heavy ships out of the narrows.",
          "keys": ["chr:scene:actium-campaign-31bc#6.2"],
          "basis": "sourced",
          "estSeconds": 5.5
        }
      ]
    }
  ]
}
```

- `kind` is one of:
  - `narration`: voices statements;
  - `transition`: no claim, and no `keys`;
  - `quote`: reads a quotation verbatim, and adds `voice`, the `locator` it reads.
- `basis` is the weakest basis among the line's `keys`. A line keyed to a sourced and an inferred statement is `inferred`, and is worded as such.
- `estSeconds` lets the player hold each step until its narration ends. The step advances when its last line has played, not on a timer.
- `persona` is optional:
  - `browser`: no locators;
  - `student`: the source named in most lines;
  - `scholar`: locators read where they help.

## 5. When the scene changes

The scene is rebuilt from the graph and can change. Statement ids are positional (`#<step>.<n>`), so they renumber when a statement is added. Always record `sceneContentHash`. If it no longer matches the scene's `contentHash`, the narration is stale: the player marks it, and it must be regenerated for the steps whose statements changed.

Chrystallum's own narrator (`narrative/narrate_scene.py`) does this by step: a narration records a fingerprint of each step it was written from (`stepHashes`), and a re-run sends only the steps whose fingerprint changed. Every other step keeps its lines word for word, so its voiced clips stay valid. An app narrating from outside should do the same: return lines only for the steps that changed, and keep the rest.

## 6. What the narration is, in Chrystallum's terms

A narration is a **made** presentation of the scene, never evidence. It is never written into the graph as a claim, and it never cites itself.

A generated voice recording counts as a made media item (26a, shape 8, `kind: audio`). `narrative/voice_scene.py` voices a checked narration one clip per line through the ElevenLabs API and writes the record, `audio.json`, beside the clips: generator, model, voice, the narration file and its hash, the scene's `contentHash`, and each line's written and spoken text. Names are respelled for the voice from `curation/pronunciations.json`; captions keep the written name. Use a stock or designed voice, never one that imitates a real person. The clips are not committed; the player uses them only when they voice this exact narration file.
