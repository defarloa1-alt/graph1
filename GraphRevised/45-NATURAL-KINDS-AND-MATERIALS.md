---
status: decided 2026-11-18 (D-160); built: registry v18, the AAT harvest, the coin metals, Pliny's purple (§7); colour and the sails (v19); GBIF waits for a source that names a species
authority: curator, 2026-11-18 (chat): taxonomy of animals and plants, and of metals and materials, for "senator to mollusk" paths
depends_on: [30-LOGICAL-MODEL.md, 43-ACTIUM-MILITARY-FRAME.md, 44-HISTORIOGRAPHY-AND-DEBATES.md]
superseded_by: null
last_reviewed: 2026-11-18
---

# 45 — Animals, Plants, Metals and Materials

## 1. Why

Many paths between people run through things: what they wore, struck, traded,
banned, ate or wrote about. The sumptuary laws lead to purple, purple leads to
the murex, and Antony's legions lead to the silver of their pay. The model has no
place for these yet: no species, no plants, no materials. `Type` holds roles,
unit types, ship types, naval fittings and one status (41 Types); `Object` holds
single things in events (`involvedIn`, `captured`).

We already hold data for this and do not use it. Coinage of the Roman Republic
Online records a material on every coin type in our dump (1,314 silver, 145 gold,
1,143 bronze), and the coin harvest (D-151) reads the legends but ignores the
metal.

## 2. Decided (curator, 2026-11-18, D-160)

| Question | Decision |
|---|---|
| Scope | **On demand.** A species, plant or material joins when a source we hold names it, with its chain of parents up to kingdom (or to the top of the materials hierarchy), so it can be navigated upward. No bulk import of whole branches. |
| Authorities | **GBIF Backbone Taxonomy** for animals and plants (cross-checked against Catalogue of Life, which it draws on); **Getty Art & Architecture Thesaurus (AAT)** for metals, dyes and other materials. Nomisma's material ids (on the coins) are mapped to AAT. Wikidata stays a cross-reference, not the hierarchy. Licences to confirm at each authority before the first harvest. |
| First slice | **The coin metals** (from data we hold, free) and **purple and the murex** (from Pliny), then one path end to end (§5). |

## 3. Three things kept apart

1. **The modern category:** *Hexaplex trunculus*, silver, Tyrian purple. It comes
   from the authority, with its parents. It is the authority's statement, not a
   source's.
2. **The ancient word:** Pliny's *purpura*, *bucinum* and *murex*; *argentum*;
   *aurum*. This is what the source says, quoted from a passage.
3. **The identification between them:** "Pliny's *purpura* is one of the modern
   murex species". For plain cases (*argentum* is silver) it is a name
   attestation on the modern category, cited to the passage. Where scholars
   differ, as with most ancient names for animals and plants, it is a
   **Question** with **Positions** (44), never a fact. It can stay an open
   Question with no Positions until we hold a modern work that argues it.

Keeping (3) separate is what lets a path show its weak step as weak.

## 4. Model (curator, 2026-11-18: Claude's recommendations accepted)

**4.1 Kind.** Taxa and materials as `Type`, with new `typeCategory` values
`taxon`, `material`, `product` (a made thing such as a dye or a cloth) and
`denomination` (a coin's denomination: denarius, aureus, quinarius). A Type
is already "a kind of thing", so this needs no new label and leaves the graph type
(D-158) alone, apart from the new category values. The alternative, new kinds
`Taxon` and `Material`, gives them their own colour and filter in the explorer but
changes the graph type and every kind list. Decided: `Type`, with the explorer
filtering on `typeCategory`.

**4.2 New predicates (registry v18).**

| Predicate | Joins | Example | Voice |
|---|---|---|---|
| `subtypeOf` | Type → Type | *Hexaplex trunculus* subtype of Muricidae; silver subtype of precious metals | the authority (GBIF, AAT), with its record |
| `madeFrom` | Type → Type | Tyrian purple made from the murex | a source (Pliny) |
| `madeOf` | Object, Type → Type | the denarius made of silver | the coin records |
| `struckIn` | Work of form coinage → Type (denomination) | Antony's legionary coinage struck in denarii and aurei | the coin records |
| `producedAt` | Type → Place | murex purple produced at Tyre | a source |

**Colour is a property of the object** (curator, 2026-11-18), not a link to a
dye or a material. It is held as a value on the Object, through a unary claim
`hadColour` (Object, with the source's colour word as its value), as `hadStrength`
holds a count and `hadReception` a standing. The claim form keeps the source's
voice, so two sources giving different colours stay two voices.

How people meet these things (used, traded, banned, worn, paid in) is left for
after the first slice, when a real path shows which verbs are needed. Guessing
them now would give predicates nobody uses.

**4.3 The authority's hierarchy.** A `subtypeOf` copied from GBIF or AAT is the
authority's statement. Decided: they are accepted by rule, with
proposer `gbif-backbone` or `getty-aat`, as the coin-legend `instanceOf` links are
(D-145), so that 30 parent links per species do not reach the review desk. The
curator still reviews every claim a source makes about a taxon or material.

**4.4 Labels.** Every taxon shows its common name with its scientific name, e.g.
"banded dye-murex (*Hexaplex trunculus*)". A GBIF or AAT id is never shown without
its label.

## 5. The first slice

**5.1 Coin metals (free).**

1. The coin harvest adds `Material:` and `Denomination:` lines to each coin type's observation,
   taken from the dump (`nmo:hasMaterial`) with Nomisma's label.
2. The metals (silver, gold, bronze) are fetched from AAT with their parents
   (metal, precious metal) and mapped from Nomisma's ids.
3. The denominations (denarius, aureus, quinarius) become Types from the dump's
   `nmo:hasDenomination`, each proposed `madeOf` its metal and each coinage Work
   `struckIn` its denominations, quoting the coin types' `Material:` and
   `Denomination:` lines (added to the observations in step 1).

**5.2 Purple and the murex.**

1. Fetch Pliny, *Natural History* 9.124–141 (purple and its shellfish) and 19.22
   (sails), in the public-domain Bostock and Riley translation. We hold no Pliny
   passages yet. Free.
2. From GBIF: the three Mediterranean dye-murex species (*Bolinus brandaris*,
   *Hexaplex trunculus*, *Stramonita haemastoma*) with their parents; from AAT:
   Tyrian purple.
3. Proposed from Pliny: Tyrian purple `madeFrom` the murex, and `producedAt` Tyre.
   The Question "Which modern species are Pliny's *purpura* and *bucinum*?" is
   left open, with no Positions until we hold a modern work that argues it.

**5.3 One path end to end, from the Actium focus.** Pliny (19.22, to check
before use) says Cleopatra came to Actium with a purple sail and fled with it.
The path:

> Battle of Actium → Cleopatra's ship (Object, `involvedIn`) → its sail
> (Object, `hadColour` "purple", Pliny 19.22)

Because colour is a property (§4.2), the sail does not link to Tyrian purple by
being purple. Pliny also describes cheaper purples, so "dyed with Tyrian purple"
would be an inference, and it is not drawn. The sail joins the dye only if a
source we hold says what it was dyed with (`madeOf`, cited). Until then the path
from Actium to the murex has a gap at that step, and the explorer shows the gap
rather than bridging it.

## 6. Decided (curator, 2026-11-18)

1. Taxa and materials are `Type`s with new categories (§4.1).
2. Authority hierarchy links are accepted by rule (§4.3).
3. Coin denominations are Types made of their metal; a coinage is `struckIn` them
   (§4.2, §5.1).
4. Colour is a property of the object, held as the unary claim `hadColour` (§4.2).

## 7. Steps

1. **Done 2026-11-18.** Registry v18: `typeCategory` taxon, material, product,
   denomination; `subtypeOf` (attributed only: the authority's voice), `madeOf`,
   `struckIn`, `madeFrom`, `producedAt`; tests (`test_registry_v18`). Synced to the
   graph and the graph type (018) re-applied. `hadColour` is not in v18: a colour
   word is a value, and the draft schema has no free-value qualifier yet (stance and
   reception are fixed lists). It comes with the Pliny slice.
2. **Done 2026-11-18 (AAT).** `harvest/getty_aat.py` reads `curation/materials.json`
   and fetches each seed's chain from the AAT SPARQL endpoint (preserved in
   `phase-5-source/aat-*.json`; licence ODC-By 1.0, read from the AAT's own records).
   14 Types: silver, gold, nonferrous metal, metal, inorganic material, materials;
   denarius, aureus, quinarius, as (coin), Early Western World coins, coins, money,
   exchange media. 12 `subtypeOf` links, accepted by rule. The Work "Getty Art &
   Architecture Thesaurus" (form reference) is their voice. GBIF is still to do.
3. **Done 2026-11-18 (coin metals, 5.1).** `crro_coins.py <series> --metals` gives
   each coin type a second, physical record (the first is immutable, so a
   `Material:` line could not be added to it). Accepted by rule: denarius and
   quinarius made of silver, aureus made of gold (the denarius according to both
   series: "well attested"), and RRC 544 and 546 struck in their denominations.
4. **Done 2026-11-18 (Pliny, 5.2, in part).** Pliny's *Natural History* in Bostock
   and Riley (1855, public domain) preserved from Perseus. The file is TEI P4 with
   undeclared HTML entities; the Perseus adapter now resolves the entities
   (`&cdot;` is Pliny's decimal point, not HTML5's ċ) and converts P4 to the P5
   shape, recording both in the metadata. Bostock numbers by chapter: his 9.60-9.63
   are the modern 9.124-137, his 19.5 is 19.22. Migration 020 stored 9.60-9.63 and
   19.5; added Tyrian purple from the AAT (under natural dye, dye, colorant,
   accepted by rule) and Tyre (Wikidata Q82070); made Pliny's two purple shellfish
   Types of category taxon, "purpura" (also "pelagiae") and "buccinum"; and
   proposed, according to Pliny, Tyrian purple `madeFrom` each and `producedAt`
   Tyre. These are a reading, so they wait for the curator.
   **GBIF has no seed yet.** Pliny names his own kinds, not modern species, so by
   the on-demand rule (§2) no species joins until a source we hold identifies one.
   The harvester waits for that source.
   **Decided by the curator (2026-11-18), built the same day:**
   - **Colour** is a link from an object to a colour Type (`hadColour`, registry
     v19; category `colour`, from the AAT: purple → purple colors → chromatic
     colors → colors). This replaces the unary value of §4.2: it needs no new
     qualifier, keeps the source's voice, and lets the explorer find every
     purple thing. It is still the object's property and never names a dye.
   - **The sails** are an Object (migration 021), according to Pliny 19.5:
     `involvedIn` the Battle of Actium in a new role "distinguishing mark" (his
     words), `hadColour` purple, `madeOf` linen (a reading: the chapter is on dyed
     linen). Linen comes from the AAT, under textile materials.
   - **A Question about a Type** (`about` reaches Type in v19): "Which modern
     species are Pliny's purpura and buccinum?", about each, with no Positions.
5. **The path (5.3), as it stands:** Battle of Actium ← the sails (involved in) →
   purple (colour) → purple colors → … ; separately, Tyrian purple → made from
   purpura and buccinum → the open Question. No path joins Actium to the
   shellfish: the gap is at the sails, where Pliny does not say what they were
   dyed with. That is the honest result; a source we hold must close it.

6. The explorer: a `typeCategory` filter, and taxa and materials on entity cards.

Found while building:

- The AAT's per-record JSON pages fail on Getty's side (a certificate error);
  its SPARQL endpoint works, but answers 400 to a request with no `Accept`
  header.
- The AAT places the denarius under "as coins", so the graph says "denarius is
  a kind of as (coin)", according to the AAT. It is the authority's voice and is
  shown as reference only; the curator may wish to see it.
- The AAT's organizing headings (`<metal by composition or origin>`) are passed
  over and named in the quoted "Broader:" line, never made Types.

No model calls were made.
