---
status: decided 2026-11-19 (D-166); not built
authority: curator, 2026-11-19 (chat), from the Scarpus identity question
depends_on: [30-LOGICAL-MODEL.md, 44-HISTORIOGRAPHY-AND-DEBATES.md, 16-LEGACY-TRIAGE.md]
superseded_by: null
last_reviewed: 2026-11-19
---

# 46 — Roman Names and the Gens

## 1. Why

Scarpus is named three ways in what we hold: "L. Pinarius" (the heir in Caesar's
will, Suetonius, *Julius* 83), "SCARPVS IMP" (his Cyrenaica coins), and our own
entity, labelled both "Lucius Pinarius" and "Lucius Pinarius Scarpus". Whether
the heir and the commander are one man rests on how the name parts line up.
Wikidata already treats them as one: its item for Lucius Pinarius (Q382127) is
described as "nephew or grandnephew of Julius Caesar", with the alias "Lucius
Pinarius Scarpus" and cognomen Scarpus. Roman names also place a person in a
clan, which gives paths between people.

## 2. What the legacy graph did

[docs/PERSON_LOGICAL_MODEL.md](../docs/PERSON_LOGICAL_MODEL.md): every name part
from DPRR became a node (Praenomen 3,670 links, Nomen 4,619, Cognomen 3,882,
Gens 4,840, Tribe 353). Two clean-ups followed (Archive/Uncommitted-2026-11-13):
Nomen was folded into Gens as an alias (`migrate_gens_nomen_fold.py`: Sempronius
is the name form, the Sempronia the clan), and the Cognomen nodes became hubs
joining unrelated men, so labels needed life dates (`migrate_onomastic_display.py`).
Lesson: the gens is a thing; praenomen and cognomen are words.

## 3. Decided (curator, 2026-11-19)

| Question | Decision |
|---|---|
| Where name parts live | **The gens is an entity**: a `Group` (a real clan) a person belongs to, by a claim with a source. **Praenomen, nomen, cognomen and agnomen are properties** of the Person, never nodes: no "Lucius" or "Scarpus" hubs. |
| Name forms | **One label.** A person has one display label (and Wikidata aliases); name forms are not held as dated, attested claims. The Scarpus identity is argued as a Question (§5), not through name forms. |
| Sources | **Public domain first** (the product may be commercial; curator). **Wikidata** (CC0) for the structured parts and the gens, Republic and Empire; **Smith's *Dictionary of Greek and Roman Biography and Mythology*** (1849, public domain; Perseus, Wikisource) as the quotable text, entry by entry. On demand, for people already in the graph. |
| DPRR | **A switch, on by default for now** (curator, 2026-11-19; to be turned off before any commercial use). Its data is CC BY-NC 4.0 (© King's College London 2017, stated in its RDF output), so it cannot be part of a commercial product, and it covers only the Republican elite (509–31 BCE). When switched on, its records carry their rights, so an export can leave them out. |

Wikidata's properties, checked at Wikidata 2026-11-19: praenomen (P2358),
nomen gentilicium (P2359), cognomen (P2365), agnomen (P2366), gens (P5025).

## 4. Model (to build)

1. **Gens.** A `Group` with a new `groupCategory` value `gens`, from the
   Wikidata item that P5025 names (e.g. gens Pinaria, Q1453261), labelled by the
   clan's feminine form ("gens Pinaria").
2. **Membership.** A new predicate, `ofGens` (Person → Group of category gens),
   because `memberOf` requires a time and gens membership is for life. Voice:
   Wikidata (P5025) as an authority record, and Smith where his entry says it.
   Adoption (Octavian, a Julius by adoption, born an Octavius) is the case to
   test: two gentes, each with its source.
3. **Name parts.** Properties `praenomen`, `nomen`, `cognomen`, `agnomen` on the
   Person, as words (Wikidata's labels: "Lucius", "Pinarius", "Scarpus"), with
   the Wikidata revision they came from. Display only; never evidence.
4. **Smith.** An entry is a passage (SourceObservation) of the Work "Smith,
   Dictionary of Greek and Roman Biography" (form reference, 1849), quoted for
   gens, family and identity claims, as Pliny is for purple.

## 5. The first case: Scarpus

- Fetch Smith's entry for Pinarius Scarpus, Suetonius *Julius* 83 (the will),
  Dio 51.9.1 and Plutarch *Antony* 69 (his army handed to Cornelius Gallus).
- Link our Scarpus to Wikidata Q382127 (he has no Wikidata identity yet);
  take his name parts and gens Pinaria.
- Question: "Is the Lucius Pinarius of Caesar's will the Scarpus who commanded
  in Cyrenaica?", about Scarpus, with Wikidata's identification as one voice and
  Smith's as another if he gives one. No position is ours.
- Add Gaius Cornelius Gallus, and "Scarpus hands his army to Gallus"
  (Dio 51.9.1), continuing the refusal chain.

## 6. Open

- Tribe (voting tribe): a Group too, or left until a source we hold names one.
- Filiation ("L. f."): a property, or only through `childOf`.
- Whether a gens `partOf` the patriciate or plebs (status) is wanted.
