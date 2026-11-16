---
status: decided 2026-11-15; built: footnotes, registry v16, coins, Types (§7 steps 0 to 2); consistency checks and the lens run to come
authority: 41-ENDGAME-PLAN.md (D-146); docs/Response - Roman Republican Institutions and Military Hierarchies.md (decided 2026-10-13, registry v9)
depends_on: [41-ENDGAME-PLAN.md, 42-CORROBORATION-AND-CLAIM-KINDS.md, 39-LENS-SPECIALISTS.md]
superseded_by: null
last_reviewed: 2026-11-15
---

# 43 — The Military Frame for Actium, Built Before the Lens Run

## 1. Why

The battle is the focus, so the stage is set first: the kinds of unit, ship
and naval role that existed in 31 BC, so the military lens has somewhere to
place what it reads. Today a trireme or a Liburnian survives only as words in
an event label or a quotation. There are 23 role Types and no unit or ship
types, although the design for them was decided on 2026-10-13 (registry v9:
kind Type, `instanceOf`, `partOf` between Types with a quantity) and never
filled.

Prompted by a chat draft (chats/Roman Military Subgraph Schema Draft.md, an
agent that did not know the schema). Its content is taken; its labels are not.

## 2. Curator decisions (2026-11-15)

| Question | Answer |
|---|---|
| Scope | **Actium's frame**: triumviral-era legions and campaign fleets, ship types, naval roles. The Polybian template (Polybius 6, the army of about 150 years earlier) waits for the late-Republic spine. |
| Equipment | **Naval fittings only**: rams, towers, fire. Land weapons wait. |
| Coins | **Yes.** Antony's legionary denarii (32–31 BC) name his legions; Coinage of the Roman Republic Online (CRRO) makes them the first non-text evidence. **Licence (curator, 2026-11-15): Open Database License 1.0** (https://opendatacommons.org/licenses/odbl/1-0/): public reuse allowed with attribution; a database built from a substantial part of it must be shared under the same licence. We take only the coin types we need (an insubstantial part), each record keeps its `rights` (ODbL 1.0, CRRO, American Numismatic Society) like a passage, and the export carries the notice for those records. The dataset's own description ([crro/nomisma.void.rdf](crro/nomisma.void.rdf), VoID) states the licence (ODbL), the publisher (American Numismatic Society), a rights statement of no copyright in the US for the content, and the full data dump, http://numismatics.org/crro/nomisma.rdf. The site refuses automated access, so the dump comes in as a file the curator downloads into `crro/`. |

## 3. From the chat draft: taken, already ours, turned down

| Draft | Here |
|---|---|
| Type versus instance, structure valid for a period | Already ours: a Type with dated claims; a Group `instanceOf` a Type |
| `UnitType`, `RankType` | Already ours: Type (unit type, role), Office |
| `ShipType`, `EquipmentType` | **Taken** as new Type categories `ship type` and `naval fitting` |
| `Unit`, `Force`, `Ship` | Already ours: Group (a legion, a fleet, a wing), Object; a force at the battle is a Group that `participatedIn` it |
| Subunits with counts | Already ours: `partOf` between Types, with a quantity, attributed |
| Number claims with claimant, `rests_on`, claim type | Already ours: quantity qualifiers per voice; `basis` and `RESTS_ON` (D-148) |
| `precision` (exact, approximate, round, rhetorical) | **Taken** (§5) |
| Military validator rules | **Taken** into the consistency checks (41 §3.4): type norms, period, defection order, commander continuity |
| A licence per source | **Taken** (41 §3.7) |
| `EquipmentUse` node, `BEARS_ON`, side `a`/`b` | Turned down: a claim with the event as context; passages are evidence; `opposed` |

Two cautions the draft lacks. Polybius describes the manipular army of the
Hannibalic war, not the cohort legions of 31 BC. And the structure of the
large oared warships (how they were rowed and manned) is mostly modern
reconstruction: such claims carry basis `reconstructs` (42 §3), shown as a
modern reconstruction, not as fact. Wikidata is a voice here as elsewhere
(D-145): its "praefectus classis" (fleet prefect, Wikidata Q2503372) is
described as an imperial fleet commander, so a Republican use needs its own
dated claim.

## 4. The Types to seed

Seeded from Wikidata by code (labels and identifiers only, accepted by rule,
D-145); what each was, and when, comes from sources as claims.

| Category | Type (Wikidata, verified 2026-11-15) |
|---|---|
| ship type | trireme (Q208420), quadrireme (Q340066), quinquereme (Q1129014), hexareme (Q3621914), Liburnian, *liburna* (Q18843); the larger polyremes up to the "tens" (to look up) |
| unit type | Roman legion (Q163323), cohort (to look up), campaign fleet and fleet wing (ours, no Wikidata item expected) |
| role | trierarch (Q1770133, the Greek office; Roman *trierarchus* Q134014453), fleet prefect (Q2503372), marines (to look up) |
| naval fitting | naval ram (Q778702), fighting towers, fire missiles (to look up) |

"To look up" items wait on Wikidata's rate limit and are verified at the
authority before use.

## 5. Predicates and qualifiers for the curator to approve

| Name | Definition (draft) | Endpoints | Qualifiers |
|---|---|---|---|
| `hadStrength` | A force numbered a given count of ships or men at a time, as one source states it; each source's figure is its own voice, never reconciled | Group → optional Type (what is counted: a ship type, legions); none means the source's own unit | quantity required; time required; context event optional |
| `captured` | A force or person took enemy ships, men, or goods in an engagement | Group or Person → Group or Object | context event; time; quantity optional |
| `surrenderedTo` | A force or person yielded to an enemy commander | Group or Person → Group or Person | context; time required |
| `defectedTo` | A person or force left one side for the other | Group or Person → Group or Person | context; time required |

The last three are already in the predicate queue, requested by the military
and social analysts.

**Quantity precision** (`quantityPrecision` on any claim with a quantity):
`exact`, `approximate` (the source says "about"), `round` (code flags a figure
that is a multiple of 10, 100, or 1,000 for review), `rhetorical` (a reading
that a figure is a literary device: interpretation, so reviewed as reasoning).

**Proposable kinds:** the military lens may propose Type entities for its
inquiry, reviewed like any new entity.

## 6. AI synthesis: guidance and a visible voice (curator, 2026-11-15, D-149)

An agent may write a synthesis of the frame (as Copilot did for the Republican
army). It is used two ways. As **guidance**: each statement becomes an open
question with the source likely to answer it (Polybius 6.21 for maniple sizes);
a claim exists only once an agent quotes the passage. As a **visible voice**: the
synthesis is stored as a Work authored by the model (named and dated, standing
tertiary), so its statements show as "AI synthesis (unsourced)" and never add a
line of evidence. Its known faults are the reason for both rules: periods mixed
(Polybius's army as *the* Republican army), contested history stated as fact
(the "Marian reforms"), and plain errors (a cohort of four maniples; it was three).

## 7. Order of work

0. The Wikipedia footnote harvest (done 2026-11-15, D-150): the modern works the
   Actium article cites are the frame's first reading list (Lange 2011, Pelling
   1988, Murray and Petsas 1989 and Zachos 2003 on the Nikopolis monument and its
   rams; Shuckburgh 1917, cited 53 times; published in 1917, so likely public domain in
   the US, to confirm before use).
1. The curator approves §5 (registry v16). **Done 2026-11-15:** `predicates.v16.json`
   (hadStrength, captured, surrenderedTo, defectedTo; typeCategories ship type and
   naval fitting; workForm coinage) and draft schema v7 (`precision` on a quantity).
1a. **The coins (done 2026-11-15, D-151):** `python -m GraphRevised.harvest.crro_coins rrc-544
   [--apply]` reads Crawford 544 from the CRRO dump (39 types: 32 denarii, 7 aurei, 32–31 BC):
   the series as a Work (form coinage, standing primary), 39 record observations with their
   ODbL rights, 28 unit Groups (legions 1–23, 12 Antiqua, 17 Classica, 18 Libyca, the
   praetorian cohorts, the cohort of speculatores), and 28 `partOf` Proposals to "Antony's
   land forces, 32–31 BC", attributed to the coinage, for the curator to review. Titled
   legions stay apart from the plain number until the curator merges them.
2. Seed the §4 Types from Wikidata (code). **Done 2026-11-15:** `python -m
   GraphRevised.slices.seed_types GraphRevised/curation/military-types.json [--apply]`: 17 Types
   (7 ship types, 4 unit types, 3 roles, 3 naval fittings; 12 with a Wikidata identity, 5 local).
   Antony's 28 coin-named units are each `instanceOf` legion or cohort, from the legend's own
   words, accepted by rule (proposer `crro-coin-legend`, D-145); their service in his forces
   stays the curator's to review.
3. Antony's named legions as Groups, from the sources (and from coins, if the
   CRRO licence allows public reuse).
4. The first consistency checks (41 §3.4) over people, the Years, and these
   Types.
5. Then the lens run (41 phase 1), ancient sources first.
