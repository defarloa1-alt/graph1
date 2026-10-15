# Weaving Neo4j Work Annotations into an Actium Narrative

## Direct answer

A `CONCERNS` relationship should not determine the order of the story. It says that a work is relevant to an entity; it does not say **when that entity enters the narrative**, **which claim the work supports**, or **where the passage belongs in a causal sequence**.

For the Battle of Actium, the narrative should be built from ordered **narrative units**—strategic prelude, blockade, decision, deployment, engagement, breakout, collapse, and aftermath. Each unit can then be annotated with the entities it mentions, the assertions it expresses, and the works or passages that discuss those entities or support those assertions.

## The sequencing distinction

Three forms of order need to be kept separate:

| Order | What it answers | Appropriate graph structure |
|---|---|---|
| Historical chronology | What happened before or after what? | `Event` or `Phase` connected by `PRECEDES`, `FOLLOWS`, `PART_OF`, and dated intervals |
| Narrative order | In what order should the reader encounter the material? | `NarrativeUnit.sequence`, `NEXT`, or membership in an ordered `Narrative` |
| Documentary order | Where does the evidence occur in a work? | `Passage.start`, `Passage.end`, chapter/section citations, or `NEXT_PASSAGE` |

`(:Work)-[:CONCERNS]->(:Entity)` belongs to none of these ordering systems. It is an **aboutness/indexing relationship**. A biography of Antony may concern Antony throughout, concern Actium in several chapters, and concern Cleopatra in scattered passages; none of those edges tells the narrative generator where to place the information.

A useful rule is:

> **Entities are mentioned; assertions are stated; passages provide evidence; works concern subjects; narrative units are sequenced.**

## Suggested narrative layer

A minimal narrative layer could look like this:

```text
(:Narrative {id, title})
  -[:HAS_UNIT {position: 1}]->
(:NarrativeUnit {
    id,
    unitType,          // orientation, cause, action, turning_point, outcome
    sequenceKey,
    text,
    startDate,
    endDate
})

(:NarrativeUnit)-[:MENTIONS]->(:Entity)
(:NarrativeUnit)-[:EXPRESSES]->(:Assertion)
(:Assertion)-[:SUBJECT]->(:Entity)
(:Assertion)-[:OBJECT]->(:Entity)
(:Assertion)-[:SUPPORTED_BY]->(:Passage)
(:Assertion)-[:CHALLENGED_BY]->(:Passage)
(:Passage)-[:PART_OF]->(:Work)
(:Work)-[:CONCERNS]->(:Entity)
```

If passages are not yet modeled, a `Citation` or `EvidenceItem` can temporarily occupy that role. The important point is that the narrative unit should connect to a claim or evidence-bearing passage—not merely to an entire work whose `CONCERNS` edge happens to point at the same entity.

## Example narrative

The following is a readable narrative first. The annotation blocks show what the interface might reveal when a reader expands a paragraph. They are deliberately placed **after** each narrative unit so that the story remains readable.

### Pressure before battle

By the summer of 31 BCE, Actium was not merely the location selected for a decisive naval clash. It had become a trap. Antony and Cleopatra held the southern side of the entrance to the Ambracian Gulf, while Octavian established himself on the heights to the north and used his fleet to restrict movement by sea. Agrippa intensified the pressure by taking Methone and later striking Leucas, Patrae, and Corinth, disrupting communications and supplies before the principal engagement.[^1][^2][^3]

**Annotation A1 — strategic isolation**

```yaml
narrativeUnit: actium-01-strategic-isolation
sequence: 10
unitType: strategic_prelude
mentions:
  - Battle of Actium
  - Marcus Vipsanius Agrippa
  - Mark Antony
  - Cleopatra VII
  - Octavian
  - Ambracian Gulf
expresses:
  - Agrippa's preliminary operations weakened Antony's strategic position.
  - Octavian's forces constrained Antony by land and sea.
evidence:
  - work: Cassius Dio, Roman History, Book 50
    passage: 50.11.3; 50.12.1-8; 50.13.5
    type: primary_source
    kind: narrative_history
  - work: Velleius Paterculus, Roman History, Book 2
    passage: 2.84.2
    type: primary_source
    kind: narrative_history
concerns:
  - Battle of Actium
  - Marcus Vipsanius Agrippa
```

This annotation does not mean that Dio or Velleius should appear first because their works concern Agrippa. It means that the cited passages are attached to the first narrative unit because they support claims about the **strategic prelude**.

### Attrition and decision

Conditions in Antony's position deteriorated. Ancient accounts emphasize sickness, desertion, inadequate crews, and shortages, although they differ in tone and explanation. Antony's council therefore faced a choice between remaining, seeking battle on land, or using the fleet to force an escape; Plutarch presents Canidius as favoring a land battle, while Dio says Cleopatra persuaded the council to prepare a movement toward Egypt disguised as a naval engagement.[^4][^1]

**Annotation A2 — decision under pressure**

```yaml
narrativeUnit: actium-02-war-council
sequence: 20
unitType: decision
mentions:
  - Mark Antony
  - Cleopatra VII
  - Publius Canidius Crassus
expresses:
  - Antony's command considered abandoning the Actium position.
  - The intended purpose of the naval operation is disputed.
interpretiveStatus: contested
interpretations:
  - decisive_battle_then_escape
  - planned_breakout
  - flight_after_battle_turned
sources:
  - Plutarch, Life of Antony 63-64
  - Cassius Dio, Roman History 50.14-15
```

The contested interpretation should be explicit. A modern narrative need not choose between “battle” and “breakout” too early: Antony could have sought a tactical success that would open the route for a strategic withdrawal. A Cornell discussion of Barry Strauss's interpretation likewise presents the departure of Cleopatra's squadron as part of a prior plan rather than spontaneous betrayal, while acknowledging the familiar rival tradition.[^2]

### Deployment

On 2 September 31 BCE, Antony's fleet moved toward the mouth of the gulf. Cleopatra's squadron of sixty ships remained behind the main fighting line, positioned so that it could exploit an opening. Opposite them, Agrippa exercised the principal naval command for Octavian, while subordinate commanders controlled portions of the line; the ancient sources do not describe every command arrangement in exactly the same way.[^5][^4]

**Annotation A3 — forces deployed**

```yaml
narrativeUnit: actium-03-deployment
sequence: 30
unitType: military_deployment
mentions:
  - fleet of Antony and Cleopatra
  - fleet of Octavian
  - Marcus Vipsanius Agrippa
  - Cleopatra's squadron
expresses:
  - Cleopatra's squadron was positioned behind the principal battle line.
  - Agrippa held senior responsibility for Octavian's naval operations.
sourceAgreement: partial
```

This is where precise predicates matter. `Agrippa COMMANDED Octavian's fleet` may be acceptable as a broad summary, but a richer model should distinguish `HELD_OVERALL_NAVAL_COMMAND`, `COMMANDED_WING`, and `EXERCISED_AUTHORITY_UNDER_AUSPICES_OF`. Velleius assigns Agrippa charge of the naval conflict while naming Lurius and Arruntius as wing commanders.[^5]

### The lines engage

For a time the fleets faced one another without closing decisively. Plutarch says that part of Antony's line eventually moved forward and that Octavian's ships drew it farther from the gulf; the battle then became less like a sequence of clean ramming attacks than a close struggle around high-sided ships, fought with missiles, grappling, and boarding attempts. Agrippa extended his wing, threatening to envelop his opponents and stretching the opposing formation.[^4]

**Annotation A4 — engagement and extension**

```yaml
narrativeUnit: actium-04-engagement
sequence: 40
unitType: combat_action
mentions:
  - Marcus Vipsanius Agrippa
  - Octavian's fleet
  - Antony's fleet
expresses:
  - Agrippa extended a wing of Octavian's formation.
  - The extension contributed to separation and disorder in Antony's line.
claimsRequirePassageEvidence: true
```

Notice that “Agrippa concerns Battle of Actium” is not enough to generate this paragraph. The paragraph requires event-specific assertions: who extended which formation, against whom, at what stage, and with what reported effect.

### Cleopatra breaks through

At the critical moment, Cleopatra's squadron raised sail and passed through or beyond the engaged formations toward the open sea. This action is secure at the broad level, but its meaning is not. Plutarch and Velleius frame it as flight, whereas a planned-breakout reading treats the movement as the execution of the withdrawal already discussed before the battle.[^2][^4][^5]

**Annotation A5 — pivotal movement**

```yaml
narrativeUnit: actium-05-cleopatra-breakout
sequence: 50
unitType: turning_point
mentions:
  - Cleopatra VII
  - Cleopatra's squadron
  - Ionian Sea
expresses:
  - Cleopatra's squadron departed the battle area toward the open sea.
assertionStatus: accepted_broad_fact
interpretationStatus: disputed
sourceFramings:
  Plutarch: flight that disrupted Antony's fleet
  Velleius: blame-centered desertion
  modern_breakout_reading: prearranged strategic withdrawal
```

The graph should therefore separate the observation from its interpretation:

```text
Assertion 1: Cleopatra's squadron sailed out through the battle area.
Assertion 2: Cleopatra fled because the battle was lost.
Assertion 3: Cleopatra executed a prearranged breakout.
```

Assertion 1 can receive strong multi-source support. Assertions 2 and 3 should remain competing explanatory claims, each linked to its evidence and scholarly advocate.

### Antony follows

Antony then left the main action and followed Cleopatra with a portion of his available ships. Hostile ancient narratives portray the act as personal and shameful abandonment; a strategic reading treats it as continuation of the attempted breakout. Either way, his departure deprived the forces remaining at Actium of their highest political and military leader at the decisive moment.[^4][^5]

**Annotation A6 — command departure**

```yaml
narrativeUnit: actium-06-antony-departs
sequence: 60
unitType: turning_point
mentions:
  - Mark Antony
  - Cleopatra VII
expresses:
  - Antony departed the principal engagement after Cleopatra's squadron.
  - Antony's remaining naval forces continued fighting without him.
framing:
  neutralNarrative: departed and followed
  Plutarch: abandoned his forces under Cleopatra's influence
  Velleius: deserted his fighting soldiers
```

This illustrates why wording in the generated narrative should be attached to a **framing annotation**. “Followed,” “withdrew,” “escaped,” “fled,” and “deserted” can refer to substantially the same movement while embedding very different judgments.

### Fighting continues

The battle did not end when Antony and Cleopatra escaped. The remaining ships continued to resist. Plutarch compares the fighting around the large vessels to assaults on fortified positions, while Dio gives a much more elaborate account of missiles, boarding attempts, and fire consuming ships and crews. Plutarch reports fewer than five thousand dead and attributes to Octavian a claim of three hundred captured ships, but such figures should be stored as source-attributed claims rather than unqualified database facts.[^6][^1][^4]

**Annotation A7 — resistance and loss**

```yaml
narrativeUnit: actium-07-remaining-fleet
sequence: 70
unitType: combat_outcome
mentions:
  - Antony's remaining fleet
  - Octavian's fleet
expresses:
  - Fighting continued after Antony's departure.
  - Octavian's forces defeated or captured the remaining fleet.
quantifiedClaims:
  - value: fewer than 5000
    measure: deaths
    assertedBy: Plutarch, Life of Antony 68.1
  - value: 300
    measure: ships captured
    assertedBy: Octavian as reported by Plutarch
```

The nested attribution in the ship total matters: it is not merely “Plutarch says 300.” It is “Plutarch reports that Caesar/Octavian wrote that 300 were captured.” That can be modeled with an assertion about another assertion or with `quotedSource` and `reportedBy` roles.

### The army yields

The land army did not instantly dissolve. Plutarch says Antony's soldiers remained together for seven days, hoping for his return, before surrendering after Canidius departed and their position became untenable. Dio likewise places the reduction of the remaining forces after the naval victory, while Velleius compresses the process into a moralized account of capitulation following the commanders' flight.[^7][^6][^5]

**Annotation A8 — campaign outcome**

```yaml
narrativeUnit: actium-08-surrender
sequence: 80
unitType: aftermath
mentions:
  - Antony's land army
  - Publius Canidius Crassus
  - Octavian
expresses:
  - Antony's land forces remained organized after the naval defeat.
  - The army subsequently surrendered to Octavian.
temporalRelation:
  after: actium-07-remaining-fleet
  delayClaim:
    duration: seven days
    source: Plutarch, Life of Antony 68.3
```

The result was decisive not simply because ships had been burned or captured, but because Antony lost the concentrated military position from which he had contested control of the Roman world. Octavian later presented Actium as a war won under his leadership and under the allegiance of Italy, an ideologically charged formulation preserved in the *Res Gestae*.[^8][^9]

## Reader-facing display

The prose should remain clean. A practical interface could offer three annotation depths:

- **Default view:** unobtrusive superscript markers or entity chips after each paragraph.
- **Evidence view:** a side panel showing assertions, cited passages, agreement, contradiction, and confidence.
- **Graph view:** the selected narrative unit at the center, connected to entities, assertions, passages, and works.

For example, the sentence “Agrippa extended his wing, threatening to envelop Antony's formation” could display a small marker such as **[A4]**. Selecting it would show:

```text
Narrative unit: Engagement and extension
Entity mentions: Agrippa; Antony's fleet; Octavian's fleet
Assertion: Agrippa extended the left wing against the opposing formation
Evidence: Plutarch, Life of Antony 66.2-3
Work metadata: primary_source / biography
Work concerns: Agrippa; Antony; Battle of Actium
Confidence: high that Plutarch reports it; separate confidence needed for historical actuality
```

This last distinction is essential. The graph can be highly confident that **Plutarch reports a maneuver** without assigning the same confidence to the proposition that the maneuver occurred exactly as Plutarch describes it.

## Recommended implementation

Keep the existing `Work`, `type`, `kind`, and `CONCERNS` structures, but treat them as the documentary discovery layer. Add an intermediate evidence layer and an ordered narrative layer:

```text
Work -> Passage -> EvidenceLink -> Assertion -> NarrativeUnit -> Narrative
  |                                            |
  +-------------- CONCERNS Entity              +-- sequenceKey
```

Recommended predicates are:

- `Work CONCERNS Entity` — broad topical relevance.
- `Passage MENTIONS Entity` — explicit textual occurrence.
- `Passage SUPPORTS Assertion` — positive evidentiary use.
- `Passage CHALLENGES Assertion` — contradiction or qualification.
- `NarrativeUnit EXPRESSES Assertion` — claim made by the generated prose.
- `NarrativeUnit MENTIONS Entity` — entity appearing in the prose.
- `Narrative HAS_UNIT NarrativeUnit` with `position` — editorial order.
- `HistoricalPhase PRECEDES HistoricalPhase` — historical sequence independent of prose order.

Do not place `sequence` on `CONCERNS`. The same work may concern the Battle of Actium globally and support several nonadjacent narrative units. Ordering the edge would incorrectly imply that aboutness itself has a single position in the story.

## Practical conclusion

For Actium, the most stable narrative spine is:

1. Agrippa isolates Antony's position.
2. Shortages, sickness, and desertion narrow Antony's choices.
3. Antony's council adopts a naval operation with escape toward Egypt at least as a contingency.
4. The fleets deploy outside the gulf.
5. The lines engage and extend.
6. Cleopatra's squadron breaks through.
7. Antony follows with part of the fleet.
8. The remaining ships continue fighting and are defeated.
9. The land army subsequently surrenders.

The `Work-CONCERNS-Entity` annotations can appear throughout that story, but the story should be sequenced by these event and argument units. The annotations then explain **who is present, what is being claimed, which passage supports it, how the source frames it, and where interpretations diverge**.

---

## References

1. [Cassius Dio — Book 50](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Cassius_Dio/50*.html) - The following is contained in the Fiftieth of Dio's Rome:— 1. How Caesar and Antony began hostilitie...

2. [Historian delves into the battle that shaped the Roman Empire](https://history.cornell.edu/news/historian-delves-battle-shaped-roman-empire) - Agrippa was Octavian's indispensable commander, who won not only the Battle of Actium but the six-mo...

3. [Velleius Paterculus : Book 2 ( Shipley )](http://www.yorku.ca/pswarney/4130/Velleius%20Paterculus%20%20Book%202%20(%20Shipley%20).htm) - – Then, in the consulship of Caesar and Messala Corvinus, the decisive battle took place at Actium. ...

4. [Plutarch • Life of Antony](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Plutarch/Lives/Antony*.html) - As he was getting ready for the Parthian war, he sent to Cleopatra, ordering her to meet him in Cili...

5. [LacusCurtius • Velleius Paterculus — Book II, Chapters 59‑93](https://penelope.uchicago.edu/Thayer/e/roman/texts/velleius_paterculus/2c*.html) - the decisive battle took place at Actium. The victory of the Caesarian party was a certainty long be...

6. [Plutarch, Life of Antony 68](https://lexundria.com/plut_ant/68/prr) - 68This, then, was the situation of Antony. But at Actium his fleet held out for a long time against ...

7. [Cassius Dio — Book 51](https://penelope.uchicago.edu/Thayer/e/roman/texts/cassius_dio/51*.html) - The following is contained in the Fifty-first of Dio's Rome:— 1. How Caesar after his victory at Act...

8. [Augustus, Res Gestae](https://www.livius.org/sources/content/augustus-res-gestae/) - I gave the people the spectacle of a naval battle beyond the Tiber, at the place where now stands th...

9. [The Deeds of the Divine Augustus](https://classics.mit.edu/Augustus/deeds.html) - I gave the people a spectacle of a naval battle, in the place across the Tiber where the grove of th...

